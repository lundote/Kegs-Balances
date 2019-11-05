#! /usr/bin/env/ python
import logging
from src import EkosSelenium
from src import renamefile
from src import datareformat
from src import sendemail
import yaml
from datetime import date

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create file handler
fh = logging.FileHandler('Kegs-Balances/kegsbalances.log') # PATH to file on local machine
fh.setLevel(logging.INFO)
# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Add formatter to fh
fh.setFormatter(formatter)
# Add fh to logger
logger.addHandler(fh)

# Initialize classes
ekos = EkosSelenium.EkosSelenium()
rename = renamefile.RenameFile()
reformat = datareformat.DataReformat()
email = sendemail.SendEmail()

# Define variables
# Config
conf_file ='./config_EXAMPLE.yaml' #PATH to config file
stream = file(conf_file, 'r')
config = yaml.safe_load(stream)

# Ekos
eUsername = config['ekos_user']
ePassword = config['ekos_pw']
PATH = config['PATH']	# PATH on local machine
empties = 'Kegs At Customers - Pivoted by Keg Type/Quantity [Script Report]'
overdue_bals = 'Invoice - Overdue Balances Summed by Company'
today = date.today()

# Send email
message = 'Attached you\'ll find two reports: \n\n'
message += '1. Empties.csv -- details accounts with empty kegs that have not '
message += 'ordered within the last 30 days. \n'
message += '2. OverdueBalances.csv -- details accounts with balances that are'
message += ' newly overdue, have been overdue, or are pending a credit hold. \n\n'
message += 'Please address any questions regarding balances to Amelia. If you\'re'
message += ' experiencing technical problems with this email, please contact Lund.'
subject = 'Updated Empties and Overdue Balances: %s' % str(today.replace(day=today.day))
emailTo = config['email_list']
emailFrom = config['email_user']
password = config['email_pw']

try:
	# Ekos login
	ekos.login(eUsername, ePassword)

	# Download and rename empties report
	r1time = ekos.download_report(empties)
	rename.rename_file(empties+'.csv', PATH)
	# Download and rename Overdue Balances report
	r2time = ekos.download_report(overdue_bals)
	rename.rename_file(overdue_bals+'.csv', PATH)

	# Quit Ekos
	ekos.quit()

	# Reformat Data
	reformat.data_reformat_empties(PATH, 'empties.csv')
	reformat.data_reformat_overdue(PATH, 'overdue_bals.csv')
except Exception as e:
	ekos.quit()
    logger.error(e, exc_info=True)