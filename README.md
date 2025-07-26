<h1 align="center">
  <a href="https://duoxpy.site">
    <img src="https://github.com/Chromeyc/DuoXPy-Stripe/blob/main/images/transparent_banner.png?raw=true" alt="DuoXPy Stripe Banner" height="160" />
  </a>
</h1>

<p align="center"><i>The ultimate Stripe-integrated subscription bot for Discord 💳</i></p>

<p align="center">
  <a href="https://github.com/Chromeyc/DuoXPy-Stripe/graphs/contributors">
    <img src="https://img.shields.io/github/contributors-anon/Chromeyc/DuoXPy-Stripe?style=flat-square">
  </a>
  <a href="./LICENSE">
    <img src="https://img.shields.io/badge/license-Custom-lightgrey.svg?style=flat-square">
  </a>
</p>

<p align="center">
  <a href="https://discord.gg/pu9uDNVMHT">
    <img src="https://img.shields.io/badge/chat-on%20discord-7289da.svg?style=flat-square&logo=discord">
  </a>
  <a href="https://github.com/Chromeyc/DuoXPy-Stripe">
    <img src="https://img.shields.io/github/stars/Chromeyc/DuoXPy?style=social" alt="GitHub stars">
  </a>
</p>

---

## 🌐 About DuoXPy Stripe

**DuoXPy Stripe** is a Discord bot that allows users to purchase subscriptions using **Stripe checkout links**. With an interactive purchase system and license key delivery, this bot automates your selling flow while keeping everything smooth, fast, and secure.

> 💡 **Note**: This tool is for educational and personal use only. Commercial resale is prohibited.

---

## ⚙️ Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/Chromeyc/DuoXPy-Stripe.git
cd DuoXPy
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables. Create a `.env` file and add the following:

```dotenv
DISCORD_TOKEN=your_discord_bot_token
STRIPE_API_KEY=your_stripe_api_key
STRIPE_ENDPOINT_SECRET=your_stripe_endpoint_secret
```

4. Configure your Stripe products and price IDs (see below).
5. Run the bot:

```bash
python bot.py
```

---

## 🚀 Features

* 🛒 `/purchase` command for subscription checkout
* 🎟️ Auto-generated Stripe checkout links
* 🔐 Secure license key generation & delivery
* 📟 License data stored in JSON
* ⚙️ Stripe webhook integration for post-purchase flow
* 📊 Ready to expand with more products or Robux options

---

## 💳 Stripe Integration

1. Go to your **Stripe Dashboard**
2. Navigate to **Products** > **Add Product**
3. Create entries for:

   * 1 Month (\$2)
   * 3 Months (\$5)
   * 6 Months (\$7)
   * 12 Months (\$15)
   * Lifetime (\$20)
4. Get the `price_id` for each product and add them to your `get_stripe_price_id()` function.

---

## 📦 Example Licenses

Your `licenses.json` stores user licenses in the following format:

```json
{
  "customer_id_1": "license_key_ABC123",
  "customer_id_2": "license_key_DEF456"
}
```

> You can replace this with MongoDB if needed for scalability.

---

## 🔧 To-Do

* [x] Im not gonna do anything for this anymore.

---

## 🧪 Development

Built with:

* 🐍 Python 3.11
* 🤖 Discord.py
* 💸 Stripe API
* 📁 JSON for license management (Mongo optional)

---

## 💬 Community

Have questions or want to share feedback? Join our Discord:

[![Discord](https://img.shields.io/badge/discord-join%20now-7289da?style=for-the-badge\&logo=discord)](https://discord.gg/pu9uDNVMHT)

---

## 📜 License

This project is licensed under the [DuoXPy License](./LICENSE).
**Strictly no resale or commercial use.**

---

<p align="center">
  <i>Crafted with ❤️ by <a href="https://github.com/Chromeyc">Chromeyc</a></i>
</p>
