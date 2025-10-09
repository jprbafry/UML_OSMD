cd uml
pwd
java -jar ~/plantuml/plantuml.jar -tsvg *.txt # & PID=$!; sleep 10; kill $PID
java -jar ~/plantuml/plantuml.jar *.txt # & PID=$!; sleep 10; kill $PID
mv *.svg ../img/svg
mv *.png ../img/png
cd ..

