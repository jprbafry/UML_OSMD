# UML OSMD

This repo contains examples of UML diagrams generated with PlantUML

## Installing PlantUML pre-requisites
```
sudo apt install graphviz
sudo apt install default-jdk -y
```

## Cloning/Building PlantUML
```
# Go to home directory
cd

# Clone and build plantUML
git clone https://github.com/plantuml/plantuml.git

# Enter PlantUML directory
cd plantuml/

# Build PlantUML
gradle build
ant
```

## Creating Diagrams
```
# to go to home directory
cd

# Go to this project's directory
cd UML_OSMD

# Run bash script that generated both *.png and *.svg images
./gen_img.sh
```
