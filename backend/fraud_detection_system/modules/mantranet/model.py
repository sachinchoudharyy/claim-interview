import numpy as np

import torch
from torch import nn

import torch.nn.functional as F

from fraud_detection_system.config import IMTFE_MODEL_PATH

from fraud_detection_system.modules.mantranet.layers import (

    ConvLSTM,

    ConvGRU,

    symm_pad,

    batch_norm,

    hardsigmoid
)

# =====================================================
# DEVICE
# =====================================================

device = torch.device(

    "cuda"

    if torch.cuda.is_available()

    else "cpu"
)

# =====================================================
# IMTFE
# =====================================================

class IMTFE(nn.Module):

    def __init__(
        self,
        in_channel=3,
        device=device
    ):

        super(IMTFE, self).__init__()

        self.relu = nn.ReLU()

        self.device = device

        # =====================================================
        # INITIALIZATION
        # =====================================================

        self.init_conv = nn.Conv2d(

            in_channel,

            4,

            5,

            1,

            padding=0,

            bias=False
        )

        # =====================================================
        # BAYAR
        # =====================================================

        self.BayarConv2D = nn.Conv2d(

            in_channel,

            3,

            5,

            1,

            padding=0,

            bias=False
        )

        self.bayar_mask = (

            torch.tensor(

                np.ones(shape=(5, 5))

            )

        ).to(self.device)

        self.bayar_mask[2, 2] = 0

        self.bayar_final = (

            torch.tensor(

                np.zeros((5, 5))

            )

        ).to(self.device)

        self.bayar_final[2, 2] = -1

        # =====================================================
        # SRM
        # =====================================================

        self.SRMConv2D = nn.Conv2d(

            in_channel,

            9,

            5,

            1,

            padding=0,

            bias=False
        )

        self.SRMConv2D.weight.data = torch.load(

            IMTFE_MODEL_PATH,

            map_location=device

        )["SRMConv2D.weight"]

        for param in self.SRMConv2D.parameters():

            param.requires_grad = False

        # =====================================================
        # FEATURE BLOCKS
        # =====================================================

        self.middle_and_last_block = nn.ModuleList([

            nn.Conv2d(
                16,
                32,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                32,
                64,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                64,
                64,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                64,
                128,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                128,
                128,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                128,
                128,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                128,
                256,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                256,
                256,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                256,
                256,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                256,
                256,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                256,
                256,
                3,
                1,
                padding=0
            ),

            nn.ReLU(),

            nn.Conv2d(
                256,
                256,
                3,
                1,
                padding=0
            )
        ])

    def forward(
        self,
        x
    ):

        _, _, H, W = x.shape

        # =====================================================
        # NORMALIZATION
        # =====================================================

        x = x / 255.0 * 2 - 1

        # =====================================================
        # BAYAR CONSTRAINTS
        # =====================================================

        self.BayarConv2D.weight.data *= self.bayar_mask

        self.BayarConv2D.weight.data *= torch.pow(

            self.BayarConv2D.weight.data.sum(

                axis=(2, 3)

            ).view(3, 3, 1, 1),

            -1
        )

        self.BayarConv2D.weight.data += self.bayar_final

        # =====================================================
        # SYMMETRIC PAD
        # =====================================================

        x = symm_pad(
            x,
            (2, 2, 2, 2)
        )

        conv_init = self.init_conv(x)

        conv_bayar = self.BayarConv2D(x)

        conv_srm = self.SRMConv2D(x)

        first_block = torch.cat(

            [

                conv_init,

                conv_srm,

                conv_bayar
            ],

            axis=1
        )

        first_block = self.relu(
            first_block
        )

        last_block = first_block

        for layer in self.middle_and_last_block:

            if isinstance(layer, nn.Conv2d):

                last_block = symm_pad(

                    last_block,

                    (1, 1, 1, 1)
                )

            last_block = layer(
                last_block
            )

        # =====================================================
        # L2 NORMALIZATION
        # =====================================================

        last_block = F.normalize(

            last_block,

            dim=1,

            p=2
        )

        return last_block


# =====================================================
# ANOMALY DETECTOR
# =====================================================

class AnomalyDetector(nn.Module):

    def __init__(
        self,
        eps=10 ** (-6),
        device=device,
        with_GRU=False
    ):

        super(AnomalyDetector, self).__init__()

        self.eps = eps

        self.relu = nn.ReLU()

        self.device = device

        self.with_GRU = with_GRU

        # =====================================================
        # LOCAL ANOMALY DETECTOR
        # =====================================================

        self.adaptation = nn.Conv2d(

            256,

            64,

            1,

            1,

            padding=0,

            bias=False
        )

        self.sigma_F = nn.Parameter(

            torch.zeros((1, 64, 1, 1)),

            requires_grad=True
        )

        self.pool31 = nn.AvgPool2d(

            31,

            stride=1,

            padding=15,

            count_include_pad=False
        )

        self.pool15 = nn.AvgPool2d(

            15,

            stride=1,

            padding=7,

            count_include_pad=False
        )

        self.pool7 = nn.AvgPool2d(

            7,

            stride=1,

            padding=3,

            count_include_pad=False
        )

        # =====================================================
        # RNN
        # =====================================================

        if not self.with_GRU:

            self.conv_lstm = ConvLSTM(

                input_dim=64,

                hidden_dim=8,

                kernel_size=(7, 7),

                num_layers=1,

                batch_first=False,

                bias=True,

                return_all_layers=False
            )

        else:

            self.conv_gru = ConvGRU(

                input_dim=64,

                hidden_dim=8,

                kernel_size=(7, 7),

                num_layers=1,

                batch_first=False,

                bias=True,

                return_all_layers=False
            )

        # =====================================================
        # FINAL
        # =====================================================

        self.end = nn.Sequential(

            nn.Conv2d(
                8,
                1,
                7,
                1,
                padding=3
            ),

            nn.Sigmoid()
        )

    def forward(
        self,
        IMTFE_output
    ):

        _, _, H, W = IMTFE_output.shape

        if not self.training:

            self.GlobalPool = nn.AvgPool2d(
                (H, W),
                stride=1
            )

        else:

            if not hasattr(self, "GlobalPool"):

                self.GlobalPool = nn.AvgPool2d(
                    (H, W),
                    stride=1
                )

        # =====================================================
        # LOCAL ANOMALY FEATURE EXTRACTION
        # =====================================================

        X_adapt = self.adaptation(
            IMTFE_output
        )

        X_adapt = batch_norm(
            X_adapt
        )

        # =====================================================
        # Z-POOL
        # =====================================================

        mu_T = self.GlobalPool(
            X_adapt
        )

        sigma_T = torch.sqrt(

            self.GlobalPool(

                torch.square(
                    X_adapt - mu_T
                )
            )
        )

        sigma_T = torch.max(

            sigma_T,

            self.sigma_F + self.eps
        )

        inv_sigma_T = torch.pow(
            sigma_T,
            -1
        )

        zpoolglobal = torch.abs(

            (mu_T - X_adapt)

            * inv_sigma_T
        )

        mu_31 = self.pool31(
            X_adapt
        )

        zpool31 = torch.abs(

            (mu_31 - X_adapt)

            * inv_sigma_T
        )

        mu_15 = self.pool15(
            X_adapt
        )

        zpool15 = torch.abs(

            (mu_15 - X_adapt)

            * inv_sigma_T
        )

        mu_7 = self.pool7(
            X_adapt
        )

        zpool7 = torch.abs(

            (mu_7 - X_adapt)

            * inv_sigma_T
        )

        input_rnn = torch.cat(

            [

                zpool7.unsqueeze(0),

                zpool15.unsqueeze(0),

                zpool31.unsqueeze(0),

                zpoolglobal.unsqueeze(0)
            ],

            axis=0
        )

        # =====================================================
        # CONV LSTM / GRU
        # =====================================================

        if not self.with_GRU:

            _, output_lstm = self.conv_lstm(
                input_rnn
            )

            output_lstm = output_lstm[0][0]

            final_output = self.end(
                output_lstm
            )

        else:

            _, output_gru = self.conv_gru(
                input_rnn
            )

            output_gru = output_gru[0]

            final_output = self.end(
                output_gru
            )

        return final_output


# =====================================================
# MANTRANET
# =====================================================

class MantraNet(nn.Module):

    def __init__(
        self,
        in_channel=3,
        eps=10 ** (-6),
        device=device,
        with_GRU=False
    ):

        super(MantraNet, self).__init__()

        self.eps = eps

        self.relu = nn.ReLU()

        self.device = device

        self.IMTFE = IMTFE(

            in_channel=in_channel,

            device=device
        )

        self.AnomalyDetector = AnomalyDetector(

            eps=eps,

            device=device,

            with_GRU=with_GRU
        )

    def forward(
        self,
        x
    ):

        return self.AnomalyDetector(
            self.IMTFE(x)
        )