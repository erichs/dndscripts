### D&D Scripts Repository

This project builds a local docker image that can be used to run several D&D-related scripts and utilities.

### Getting Started
1. [Install Docker](https://www.docker.com/get-started/).
2. Clone this repository.
3. Build: `cd dndscripts && docker build . -t dndscripts:latest`
4. Put `dndscripts.sh` in your PATH.

### Generating Images for an Adventurer's League PDF

![ALPDF-to-TokenPDF](https://theparchmentpaladin.com/img/2gU3aDmxIL-550.avif)

1. `mkdir DDAL && cd DDAL`	
2. Download your AL PDF, many can be found on [DMsGuild](https://www.dmsguild.com/browse.php?filters=45470_0_0_0_0_0_0_0&src=fid45470). Save it in the DDAL dir. Let's say it is `DDAL-FOO-7.pdf`
3. export OPENAI_API_KEY=<sk-your-api-key...>
3. `./dndscripts.sh alcreatures /opt/DDAL-FOO-7.pdf`

This will:
* extract the creatures listed from the statblocks section
* generate appropriate and thematic images in the DDAL dir for each creature
* gather an approximate count of creature tokens you would need to run the adventure
* name the image files appropriately

### Cropping Creature Images to Circle Tokens

Intended to be run after the `alcreatures` script, but can be run anytime your current directory contains image files that follow the same naming convention, e.g. `mimic_medium_1in_1ct.webp`.

1. `cd DDAL`
2. `./dndscripts.sh crop`

This will create a `cropped` dir, containing circle-cropped token images of all the images found in the DDAL dir, sized according to their creature size: 1 inch for small/medium, 2 inches for large, etc. You can use these in VTTs as-is, or proceed to the next script if printing for tabletop use.

### Layout a PDF for printing

1. `cd DDAL`
2. `./dndscripts.sh pdf`

This will pack the appropriate number of tokens (based on the filenames found in the `cropped` dir) into a PDF appropriate for printing, cutting or stamping out, and using at the table!
