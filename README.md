#### SIMPLE TEMPORAL CHATBOT

#### How to run the chatbot:
1. Clone the repository
2. Run the following command in the terminal:
```
pip install -r requirements.txt
```
3. Run the following command in the terminal to start Temporal server:
```
temporal server start-dev
```
4. Run the following command in the terminal to start websocket server:
```
python server.py
```
5. Run the following command in the terminal to start ChatWorkflow worker:
```
python worker.py
```
6. Run the following command in the terminal to start the chatbot client:
```
python async_client.py
```
7. Type something then press Enter.

