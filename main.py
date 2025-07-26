import discord
from discord import app_commands
from discord.ext import commands
import stripe
import json
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Add after load_dotenv()
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise ValueError("No Discord token found in .env file")

stripe_key = os.getenv("STRIPE_API_KEY")
if not stripe_key:
    raise ValueError("No Stripe API key found in .env file")

# Initialize stripe with proper error handling
try:
    stripe.api_key = stripe_key
except Exception as e:
    print(f"Error initializing Stripe: {e}")
    exit(1)

# Initialize bot with all required intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.dm_messages = True

PENDING_PAYMENTS = {}  # Store session IDs and their details
LAST_PURCHASE_TIME = {}  # Store the last purchase time for each user

class PaymentMethodView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Stripe", style=discord.ButtonStyle.primary, custom_id="stripe")
    async def stripe_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Remove the DM check since we want this to work in DMs
        await show_subscription_options(interaction)

    @discord.ui.button(label="Robux", style=discord.ButtonStyle.secondary, disabled=True, custom_id="robux")
    async def robux_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Robux payments are not available yet!")

class SubscriptionSelect(discord.ui.Select):
    def __init__(self):
        # Check available licenses and prices
        licenses = load_licenses()
        prices = {
            "1_month": ("1 Month - €2", "price_1QqMmFFHLfS0U7MgL4mnpv4v"), # replace all these with ur price id's
            "3_month": ("3 Months - €5", "price_1QqMmoFHLfS0U7Mgl5027diR"),
            "6_month": ("6 Months - €10", "price_1QqMnCFHLfS0U7MgJYAM57G1"),
            "12_month": ("12 Months - €15", "price_1QqMnRFHLfS0U7MgstEXyi0n"),
            "lifetime": ("Lifetime - €20", "price_1QqMndFHLfS0U7MgpHCQZrR4")
        }
        
        # Create options for all durations
        valid_options = []
        for duration, (label, price_id) in prices.items():
            if duration in licenses and licenses[duration]:
                valid_options.append(
                    discord.SelectOption(
                        label=label,
                        value=duration,
                        description=f"{len(licenses[duration])} keys available"
                    )
                )
        
        if not valid_options:
            valid_options.append(
                discord.SelectOption(
                    label="No options available",
                    value="none",
                    description="Please contact support"
                )
            )

        super().__init__(
            placeholder="Select subscription duration",
            options=valid_options,
            min_values=1,
            max_values=1,
            disabled=not valid_options or valid_options[0].value == "none"
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "none":
            await interaction.response.send_message(
                "No subscription options are currently available. Please contact support."
            )
            return

        duration = self.values[0]
        try:
            # Check license availability first
            licenses = load_licenses()
            if not licenses.get(duration) or len(licenses[duration]) == 0:
                await interaction.response.send_message(
                    f"Sorry, no licenses available for {duration} duration. Please try another option or contact support."
                )
                return

            # Create Stripe payment with currency-compatible payment methods
            price_id = get_stripe_price_id(duration)
            session = stripe.checkout.Session.create(
                payment_method_types=[
                    "card",          # Universal
                    "link",          # Universal
                    "paypal",        # Supports EUR
                    "bancontact",    # Supports EUR
                    "eps",           # Supports EUR
                    "klarna"         # Supports EUR
                ],
                payment_method_options={
                    "card": {
                        "request_three_d_secure": "automatic"
                    }
                },
                line_items=[{
                    "price": price_id,
                    "quantity": 1
                }],
                mode="payment",
                success_url="https://discord.com/channels/@me",
                cancel_url="https://discord.com/channels/@me",
            )
            
            # Reserve the license key
            PENDING_PAYMENTS[session.id] = {
                "user_id": interaction.user.id,
                "duration": duration,
                "timestamp": time.time(),
                "reserved_key": licenses[duration][0]  # Reserve the first available key
            }
            
            embed = discord.Embed(
                title="Complete Your Purchase",
                description="1. Click the payment link below\n2. After payment, click the Verify button (Link Expires in 24 Hours)\n3. If the button expires, use `/verify`",
                color=discord.Color.blue()
            )
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Payment Link", value=session.url, inline=False)
            embed.add_field(name="Session ID", value=session.id, inline=False)
            
            # Create view with verify button
            view = PurchaseView(session.id)
            
            await interaction.response.edit_message(embed=embed, view=view)

        except Exception as e:
            await interaction.response.send_message(
                "There was an error processing your request. Please try again later."
            )
            print(f"Error: {e}")

class SubscriptionView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SubscriptionSelect())

def get_stripe_price_id(duration):
    prices = {
        "1_month": "price_1QqMmFFHLfS0U7MgL4mnpv4v", # replace all these with ur price id's (found on the product details)
        "3_month": "price_1QqMmoFHLfS0U7Mgl5027diR",
        "6_month": "price_1QqMnCFHLfS0U7MgJYAM57G1",
        "12_month": "price_1QqMnRFHLfS0U7MgstEXyi0n",
        "lifetime": "price_1QqMndFHLfS0U7MgpHCQZrR4"
    }
    
    price_id = prices.get(duration)
    if not price_id:
        raise ValueError(f"Price ID for duration {duration} not configured yet")
    return price_id

async def show_subscription_options(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Select Subscription Duration",
        description="Choose how long you want to subscribe for:",
        color=discord.Color.blue()
    )
    view = SubscriptionView()
    await interaction.response.edit_message(embed=embed, view=view)

class DuoShopBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="/",
            intents=intents,
            help_command=None
        )
        
    async def setup_hook(self):
        print("Bot is setting up...")
        await self.tree.sync()
        
    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print("Bot is ready!")

bot = DuoShopBot()

# Load licenses
def load_licenses():
    with open("licenses.json", "r") as file:
        return json.load(file)

# Save licenses
def save_licenses(licenses):
    with open("licenses.json", "w") as file:
        json.dump(licenses, file)

@bot.tree.command(name="purchase", description="Buy Premium Subscription")
async def purchase(interaction: discord.Interaction):
    user_id = interaction.user.id
    current_time = time.time()

    # Check if the user has an incomplete session that hasn't expired
    for session_id, data in PENDING_PAYMENTS.items():
        if data["user_id"] == user_id:
            if current_time - data["timestamp"] < 86400:  # 24 hours
                await interaction.response.send_message(
                    "You have an incomplete payment session. Please complete it or wait for it to expire (24 hours).",
                    ephemeral=True
                )
                return

    try:
        # Send initial message in channel
        await interaction.response.send_message(
            "I've sent you a DM to continue with the purchase process!",
            ephemeral=True
        )
        
        # Send payment method selection to DMs
        embed = discord.Embed(
            title="Select Payment Method",
            description="Choose your preferred payment method:",
            color=discord.Color.blue()
        )
        view = PaymentMethodView()
        await interaction.user.send(embed=embed, view=view)
        
    except discord.Forbidden:
        await interaction.response.send_message(
            "I couldn't send you a DM! Please enable DMs from server members and try again.",
            ephemeral=True
        )

class VerifyButton(discord.ui.Button):
    def __init__(self, session_id: str):
        super().__init__(
            label="Verify Payment",
            style=discord.ButtonStyle.green,
            custom_id=f"verify_{session_id}"
        )
        self.session_id = session_id

    async def callback(self, interaction: discord.Interaction):
        try:
            if self.session_id not in PENDING_PAYMENTS:
                await interaction.response.send_message("Invalid session ID or payment already claimed.")
                return

            session = stripe.checkout.Session.retrieve(self.session_id)
            
            if session.payment_status == "paid":
                payment_info = PENDING_PAYMENTS[self.session_id]
                license_key = payment_info["reserved_key"]
                duration = payment_info["duration"]
                
                try:
                    # Remove the key from available licenses
                    licenses = load_licenses()
                    if license_key in licenses[duration]:
                        licenses[duration].remove(license_key)
                        save_licenses(licenses)
                        
                        # Update original message
                        success_embed = discord.Embed(
                            title="✅ Payment Verified",
                            description="Here is your license key:",
                            color=discord.Color.green()
                        )
                        success_embed.add_field(name="Duration", value=duration)
                        success_embed.add_field(name="License Key", value=f"```{license_key}```")
                        await interaction.response.edit_message(embed=success_embed, view=None)
                        
                        # Remove from pending payments
                        del PENDING_PAYMENTS[self.session_id]
                    else:
                        await interaction.response.send_message(
                            "Error: License key no longer available. Please contact support."
                        )
                except Exception as e:
                    print(f"Error processing license: {e}")
                    await interaction.response.send_message(
                        "Error processing license. Please contact support."
                    )
            else:
                await interaction.response.send_message(
                    "Payment not completed yet. Please complete payment and try again."
                )

        except Exception as e:
            await interaction.response.send_message(
                "Error verifying payment. Please try again or contact support."
            )
            print(f"Verification error: {e}")

class PurchaseView(discord.ui.View):
    def __init__(self, session_id: str):
        super().__init__()
        self.add_item(VerifyButton(session_id))

# Add a cleanup function for expired pending payments
async def cleanup_pending_payments():
    current_time = time.time()
    expired_sessions = [
        session_id for session_id, data in PENDING_PAYMENTS.items()
        if current_time - data["timestamp"] > 3600  # 1 hour expiry
    ]
    for session_id in expired_sessions:
        del PENDING_PAYMENTS[session_id]

# Add the /verify command
@bot.tree.command(name="verify", description="Verify your payment and get your license key")
async def verify(interaction: discord.Interaction):
    user_id = interaction.user.id
    pending_sessions = [session_id for session_id, data in PENDING_PAYMENTS.items() if data["user_id"] == user_id]

    if not pending_sessions:
        await interaction.response.send_message("You have no pending payments to verify.")
        return

    for session_id in pending_sessions:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == "paid":
                payment_info = PENDING_PAYMENTS[session_id]
                license_key = payment_info["reserved_key"]
                duration = payment_info["duration"]
                
                try:
                    # Remove the key from available licenses
                    licenses = load_licenses()
                    if license_key in licenses[duration]:
                        licenses[duration].remove(license_key)
                        save_licenses(licenses)
                        
                        # Send license key to user
                        embed = discord.Embed(
                            title="✅ Payment Verified",
                            description="Here is your license key:",
                            color=discord.Color.green()
                        )
                        embed.add_field(name="Duration", value=duration)
                        embed.add_field(name="License Key", value=f"```{license_key}```")
                        await interaction.response.send_message(embed=embed)
                        
                        # Remove from pending payments
                        del PENDING_PAYMENTS[session_id]
                    else:
                        await interaction.response.send_message(
                            "Error: License key no longer available. Please contact support."
                        )
                except Exception as e:
                    print(f"Error processing license: {e}")
                    await interaction.response.send_message(
                        "Error processing license. Please contact support."
                    )
            else:
                await interaction.response.send_message(
                    "Payment not completed yet. Please complete payment and try again."
                )

        except Exception as e:
            await interaction.response.send_message(
                "Error verifying payment. Please try again or contact support."
            )
            print(f"Verification error: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))
