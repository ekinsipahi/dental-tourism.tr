import logging


logger = logging.getLogger(__name__)


def retrain_ml_model():
    from .ml import train

    return train()
