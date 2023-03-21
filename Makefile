IEEE:
	cd ./source && python3 IEEEXplore.py

Translate:
	cd ./source && python3 MarkdownTranslator.py

install:
	pip3 install selenium bs4

download:
	mkdir tmp \
		&& cd tmp \
		&& wget https://chromedriver.storage.googleapis.com/111.0.5563.64/chromedriver_mac64.zip \
		&& unzip chromedriver_mac64.zip \
		&& mv chromedriver ../ \
		&& cd .. \
		&& rm -rf tmp
	
