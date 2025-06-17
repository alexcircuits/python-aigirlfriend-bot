# Beck Bot 🤖

A Telegram bot that simulates **Guinevere Beck** from Netflix's "YOU" series. Beck responds to messages in character with her warm but slightly insecure personality, literary references, and casual texting style.

## ✨ Features

### 🎭 Character Simulation
- **Authentic Beck personality**: Warm, literary, occasionally self-deprecating
- **Natural texting style**: Short messages, contractions, casual language
- **Multilingual support**: English, Russian (informal ты), and French (informal tu)
- **Context-aware responses**: Maintains conversation history for coherent interactions

### 📊 User Analytics
- **Comprehensive user tracking**: Stores user metadata, message history, and interaction patterns
- **Entity parsing**: Automatically extracts and stores links, phone numbers, hashtags, and mentions
- **Profile photo collection**: Saves user profile pictures when available
- **Usage statistics**: Tracks message counts and entity parsing metrics

### 🛡️ Admin Controls
- **User blacklisting**: Ban and unban users with admin commands
- **Admin-only commands**: Restricted access to moderation features
- **Persistent blacklist**: Banned users stored in JSON format

### 🔧 Technical Features
- **Fireworks AI integration**: Uses LLaMA v3.1 8B model for response generation
- **Async message handling**: Non-blocking message processing
- **Data persistence**: JSON-based user data storage
- **Robust error handling**: Graceful fallbacks for API failures

## 🚀 Setup

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Fireworks AI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd beck-bot
   ```

2. **Install dependencies**
   ```bash
   pip install python-telegram-bot fireworks-ai
   ```

3. **Configure environment variables**
   ```bash
   export TELEGRAM_TOKEN="your_telegram_bot_token"
   export FIREWORKS_API_KEY="your_fireworks_api_key"
   ```

4. **Update admin configuration**
   Edit `beck.py` and add your Telegram user ID to the `ADMIN_IDS` list:
   ```python
   ADMIN_IDS = [your_user_id_here]
   ```

5. **Run the bot**
   ```bash
   python beck.py
   ```

## 📋 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_TOKEN` | Your Telegram bot token from BotFather | ✅ |
| `FIREWORKS_API_KEY` | Your Fireworks AI API key | ✅ |

### Files Created
- `user_data/`: Directory containing individual user data files
- `blacklist.json`: List of banned user IDs

## 🎮 Usage

### Basic Interaction
- **Private chats**: Beck responds to all messages
- **Group chats**: Beck responds when mentioned (@botusername) or replying to her messages
- **Character consistency**: Beck maintains her personality across all interactions

### Admin Commands
| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Initialize bot interaction | All users |
| `/ban [user_id]` | Ban a user (or reply to their message) | Admin only |
| `/unban <user_id>` | Remove user from blacklist | Admin only |
| `/blacklist` | List all banned users | Admin only |

### Example Interactions

**User**: Hey Beck, what are you reading lately?

**Beck**: oh hey! just finished rereading some Sylvia Plath... probably not the healthiest choice but you know how it is lol

what about you? any good book recs?

## 🖥️ GUI Data Viewer

The project includes a **desktop GUI application** (`guiapp.py`) for browsing and analyzing collected user data. This tool provides an intuitive interface to explore user interactions and analytics.

### 🌟 GUI Features

- **File Browser**: Search and navigate through user data files
- **Profile Viewer**: Display user metadata (username, name, language, activity timestamps)
- **Activity Statistics**: View message counts, entity parsing metrics, and chat types
- **Message History**: Browse complete conversation logs with timestamps
- **Entity Explorer**: Examine extracted links, phone numbers, hashtags, and mentions
- **Search Functionality**: Filter users by filename/identifier

### 🚀 Running the GUI

```bash
python guiapp.py
```

**Requirements**: The GUI uses Python's built-in `tkinter` library (no additional dependencies required).

### 📱 GUI Interface

The application features a tabbed interface with:

1. **Profile Tab**: Basic user information and timestamps
2. **Activity Tab**: Usage statistics and interaction metrics  
3. **Messages Tab**: Complete conversation history with Beck
4. **Entities Tab**: Parsed data (links, phones, hashtags, mentions)

Perfect for administrators who want to:
- Monitor bot usage patterns
- Analyze user engagement
- Review conversation quality
- Export user data for analysis

## 🏗️ Project Structure

```
beck-bot/
├── beck.py              # Main bot script
├── guiapp.py           # GUI data viewer application
├── blacklist.json       # Banned users list
├── user_data/          # User data storage directory
│   └── [chat_id]_[user_id].json  # Individual user files
└── README.md           # This file
```

## 🔒 Privacy & Data

The bot collects and stores:
- Basic user metadata (username, name, language)
- Message history for context
- Parsed entities (links, mentions, hashtags, phone numbers)
- Profile photos

All data is stored locally in JSON format. No data is shared with third parties beyond the AI model provider (Fireworks AI) for response generation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source. Please ensure you comply with Telegram's Bot API terms of service and Fireworks AI's usage policies.

## ⚠️ Disclaimer

This bot is a fan project inspired by the Netflix series "YOU". It is not affiliated with Netflix, the show's creators, or any official "YOU" merchandise. Use responsibly and be mindful of the character's fictional nature.

## 🛠️ Troubleshooting

### Common Issues

**Bot doesn't respond in groups**
- Ensure the bot is mentioned (@botusername) or replying to its messages
- Check that the bot has necessary permissions in the group

**API errors**
- Verify your Fireworks AI API key is valid and has sufficient credits
- Check your internet connection and API rate limits

**Permission errors**
- Ensure your user ID is correctly added to `ADMIN_IDS`
- Verify file system permissions for data directory creation

---

Built with ❤️ using Python, python-telegram-bot, and Fireworks AI 