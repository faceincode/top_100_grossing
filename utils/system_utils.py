import argparse
import smtplib

from secret.email import TOP_1000_EMAIL_ADDRESS, TOP_1000_EMAIL_PASSWORD, TOP_1000_ERROR_EMAIL_ADDRESS
from utils.record_utils import get_todays_date

# Taken from
# https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def send_error_report(error_list):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(TOP_1000_EMAIL_ADDRESS, TOP_1000_EMAIL_PASSWORD)
        subject = "Subject: T1000G Errors {}\n\n".format(get_todays_date())
        message = ""
        for error in error_list:
            message += "{}\n".format(error)
        server.sendmail(TOP_1000_EMAIL_ADDRESS, TOP_1000_ERROR_EMAIL_ADDRESS, subject + message)
        print("COMPLETED: Error Report sent.")
    except Exception as e:
        print("ERROR: Email failed to send!")