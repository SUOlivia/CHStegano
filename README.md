# CHStegano
Tool to analyse steganography data from Clone Hero's screenshots

Matt challenged me to do it, so I did it, ended up being a fun challenge

## Usage

`-a`        Analyse already dumped data with provided with `-i`

`-i`        Input screenshot or already dumped data

`-o`        Output for the data

## Examples

### Analyse screenshot without data output

`python CHStegano.py -i screenshot.png`

### Analyse screenshot with data output

`python CHStegano.py -i screenshot.png -o data.bin`


### Analyse dumped data

`python CHStegano.py -i data.bin`