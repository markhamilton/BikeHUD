This is a PyQt project designed to display vital information on a heads-up display for a bike, as well as provide PWM output for a hand-wrapped high-current AC motor.

Currently this project is in development and is only working with test data. Soon the drivers will be written to pull real data from GPIO or USB.

This was meant to run on a Beaglebone using a touch-screen shield or python-capable smartphone and a high-amp motor driver to run the bike wheel coils. You can also write custom drivers to interface with any GPIO or PC board you wish.

### SNAPSHOTS
![2013/07/03 - Screenshot](http://www.markhamilton.info/applications/bike.png)

### COMPUTER HARDWARE
* [Beaglebone](http://www.logicsupply.com/products/bb_bblk_000?gclid=CKyzt4mckLgCFRRk7Aod9VwACA) running Debian Linux
* [LCD Touch-Screen Cape](http://www.newark.com/jsp/search/productdetail.jsp?SKU=26W8118&CMP=KNC-GPLA&mckv=|pcrid|20115736341|plid|)

Alternatively, a phone capable of running python and Qt may be used instead. I am writing 2 drivers -- one to interface with an arduino using a phone's USB port, and another to directly connect using the beaglebone GPIO pins.

### SOFTWARE REQUIREMENTS
* Python 2.7 or higher
* PyQt4

### OTHER HARDWARE
* 3-Phase high-amp PWM Motor Driver.
* Neodymium Magnets.
* Magnet wire (measurements and gauge coming soon).
* Functional bike frame with tires and handlebars .
	* Pedals are optional but you will want something to rest your feet on.

### WIRING
The output of the motor driver is a 9 Amp, 300V 3-phase signal. This means you must have a multiple of 3 stator coils with an identical number of fixed magnets.

* Wiring diagrams to come.
