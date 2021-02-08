"""
Implement some function related to survival analysis
"""

import torch.nn as nn
from pycox.models import LogisticHazard
from pycox.models.loss import NLLLogistiHazardLoss


class LossAELogHaz(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        self.loss_surv = NLLLogistiHazardLoss()

    def forward(self, phi, target_loghaz):
        idx_durations, events = target_loghaz
        loss_surv = self.loss_surv(phi, idx_durations, events)

        return loss_surv


class LabelTransform:
    def __init__(self, train_durations, train_events, num_durations=10, **kwargs):
        labtrans = LogisticHazard.label_transform(num_durations)

        # fit transform with train label
        y_train_surv = labtrans.fit_transform(train_durations, train_events)
        _ = y_train_surv

        self.trans = labtrans

    def __call__(self, durations, events, **kwargs):
        """
        If list of durations and events, then return a list (batch mode).
        If only one element given for each, then, working with single element, serving as
        label_fn.
        :param durations:
        :param events:
        :param kwargs:
        :return: form (array([10]), array([1.], dtype=float32)), should convert to correct label before pass
        """
        return self.trans.transform(durations, events)


def make_label_transform_pipe(**config):
    train_df = config['train_df']
    train_durations, train_events = [train_df[o] for o in config['y_names']]
    params = {**config, 'train_durations': train_durations, 'train_events': train_events}
    label_trans = LabelTransform(**params)
    config['labtrans'] = label_trans.trans
    return config
