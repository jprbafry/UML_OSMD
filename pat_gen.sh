cd uml/pat
pwd
java -jar ~/plantuml/plantuml.jar -tsvg *.txt # & PID=$!; sleep 10; kill $PID
java -jar ~/plantuml/plantuml.jar *.txt # & PID=$!; sleep 10; kill $PID
mv *.svg ../../img/svg
mv *.png ../../img/png
cd ..



# Error line 58 in file: UML_ACT_L3C.txt
# Warning: no image in UML_CMP_RSE.txt
# Warning: no image in UML_SEQ_MGR.txt
# Error line 58 in file: UML_ACT_L3C.txt
# Warning: no image in UML_CMP_RSE.txt
# Warning: no image in UML_SEQ_MGR.txt
