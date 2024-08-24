# About  
This project is used to collect data from Telegram channels.


# How to run  
1. Install requirements with `pip install -r requirements.txt`
2. Copy `properties/clients.properties.dist` to `properties/clients.properties`.
3. Fill valid credentials into properties file. Be careful not to publish your credentials to github.
4. Modify `run.py` for your needs.
5. Run program with `python run.py`


# How to develop  
Style guide for docstrings: https://numpydoc.readthedocs.io/en/latest/format.html#overview  
Hexagonal architecture: https://vaadin.com/blog/ddd-part-3-domain-driven-design-and-the-hexagonal-architecture  
You can run tests with `python -m unittest test/cache.py`.