import logging

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.WARNING)
    #log_file = "/tmp/app.log"
    #formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    #file_handler = logging.FileHandler(log_file)
    #file_handler.setFormatter(formatter)
    #logger.addHandler(file_handler)
    return logger