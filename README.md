# About  
This project is used to collect data from Telegram channels.  

The scraper is designed to be extensible in adding new `Searches` and new `Storages`.  

`Search` is a script to iterate over desired Telegram channels and choose which data should be stored.  
`Searches` are located in `src/application/search/` directory.  

`Storage` is an adapter which accepts data row-by-row and persists it.  
`Storages` are located in `src/application/storage/` directory.  


# How to run  
1. Install requirements with `pip install -r requirements.txt`
2. Copy `properties/clients.properties.dist` to `properties/clients.properties`.
3. Fill valid credentials into properties file. Be careful not to publish your credentials to github.
4. Modify `run.py` for your needs. Create your custom `Search` or `Storage` if needed.
5. Run program with `python run.py`


# How to develop  
Style guide for docstrings: https://numpydoc.readthedocs.io/en/latest/format.html#overview  
Hexagonal architecture: https://vaadin.com/blog/ddd-part-3-domain-driven-design-and-the-hexagonal-architecture  
You can run tests with `python -m unittest discover test`.

# Citation

If you use this software in your research or project, you can cite it by referring to its official state registration certificate:
https://elibrary.ru/item.asp?id=80276645
