build:
	if [ ! -e lib/conll-rdf ]; then \
	  git clone https://github.com/acoli-repo/conll-rdf lib/conll-rdf; \
	fi; 
	./lib/conll-rdf/compile.sh

fintan:
	if [ ! -e lib/fintan ]; then \
	  git clone https://github.com/acoli-repo/fintan-backend.git lib/fintan; \
	fi;
	./lib/fintan/build.sh

