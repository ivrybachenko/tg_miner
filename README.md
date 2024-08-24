# About  
This project is used to collect data from Telegram channels.


# How to run  
1. Install requirements with `pip install -r requirements.txt`
2. Copy `properties/clients.properties.dist` to `properties/clients.properties`.
3. Fill valid credentials into properties file. Be careful not to publish your credentials to github.
4. Modify `run.py` for your needs.
5. Run program with `python run.py`


# How to develop  
You can run tests with `python -m unittest test/cache.py`.