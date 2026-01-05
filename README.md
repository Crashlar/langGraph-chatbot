# LangGraph Chatbot

This project is a chatbot application built using the LangGraph library and a Streamlit frontend. It demonstrates how to create a conversational AI with memory and persistence, showcasing different features like basic interaction, streaming responses, and database integration for conversation history.

## Features

- **Conversational AI:** A chatbot that can engage in conversations.
- **Multiple Frontend Examples:**
    - A basic chat interface.
    - An interface with streaming responses for a more interactive experience.
    - A full-featured interface with conversation history and session management.
- **LangGraph Backend:** Utilizes LangGraph for building the chatbot's logic.
- **Database Integration:** Persists conversation history in a database.
- **Easy to Run:** The project is straightforward to set up and run locally.

## Installation

Follow these steps to set up the project on your local machine.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Crashlar/langgraph-chatbot.git
    cd langgraph-chatbot
    ```

2.  **Create a virtual environment:**
    It is recommended to use a virtual environment to manage the project's dependencies.

    -   **On macOS and Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

    -   **On Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

3.  **Install dependencies:**
    Install the required Python packages using `pip` and the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

This project includes three different Streamlit frontends. You can run any of them using the `streamlit run` command.

### Basic Chatbot

This is the simplest version of the chatbot. It has a basic interface for sending and receiving messages.

To run this version, use the following command:
```bash
streamlit run streamlit_frontend.py
```

### Chatbot with Streaming

This version demonstrates how to stream the chatbot's responses to the frontend, providing a more real-time experience.

To run this version, use the following command:
```bash
streamlit run streamlit_frontend_streaming.py
```

### Chatbot with Database Integration

This is the most feature-rich version. It saves your conversation history, allows you to switch between different conversations, and start new ones.

To run this version, use the following command:
```bash
streamlit run streamlit_frontend_database.py
```

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

If you have any questions or want to get in touch, you can reach out to Mukesh Kumar at mukeshkumar.in25@gmail.com.
