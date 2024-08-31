# Bag Quests **(WIP)**

## Description
Bag Quests is a Dungeons & Dragons-inspired quest system designed for the Hack Club Slack community. It aims to streamline the process of obtaining items for another application called Bag.

## How to Use
1. To start a quest, type `/bq-start` in the Slack channel.
2. Follow the instructions provided by the bot.

## Technology Stack
- **Language**: Python
- **Libraries**: Slack SDK / Bolt
- **API**: Bag API by [rivques](https://github.com/rivques/longchain/)

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/hrushal-nikhare/bag-quests.git
    ```
2. Navigate to the project directory:
    ```sh
    cd bag-quests
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Configuration
1. Set up your Slack app and obtain the necessary tokens.
2. Create a `.env` file in the project root and add your Slack tokens:
    ```env
    SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
    SLACK_SIGNING_SECRET=your-slack-signing-secret
    BAG_ID=your-bag-id
    BAG_TOKEN=your-bag-token
    BAG_OWNER=your-bag-owner
    ```

## Running the Application
1. Start the application:
    ```sh
    python app.py
    ```

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.