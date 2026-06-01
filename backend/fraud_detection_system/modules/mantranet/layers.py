import numpy as np

import torch
from torch import nn


# =====================================================
# HARD SIGMOID
# =====================================================

def hardsigmoid(T):

    T_0 = T

    T = 0.2 * T_0 + 0.5

    T[T_0 < -2.5] = 0

    T[T_0 > 2.5] = 1

    return T


# =====================================================
# CONV LSTM CELL
# =====================================================

class ConvLSTMCell(nn.Module):

    def __init__(
        self,
        input_dim,
        hidden_dim,
        kernel_size,
        bias
    ):

        super(ConvLSTMCell, self).__init__()

        self.input_dim = input_dim

        self.hidden_dim = hidden_dim

        self.kernel_size = kernel_size

        self.padding = (
            kernel_size[0] // 2,
            kernel_size[1] // 2
        )

        self.bias = bias

        self.conv = nn.Conv2d(

            in_channels=self.input_dim + self.hidden_dim,

            out_channels=4 * self.hidden_dim,

            kernel_size=self.kernel_size,

            padding=self.padding,

            bias=self.bias
        )

        self.sigmoid = hardsigmoid

    def forward(
        self,
        input_tensor,
        cur_state
    ):

        h_cur, c_cur = cur_state

        combined = torch.cat(

            [input_tensor, h_cur],

            dim=1
        )

        combined_conv = self.conv(
            combined
        )

        cc_i, cc_f, cc_c, cc_o = torch.split(

            combined_conv,

            self.hidden_dim,

            dim=1
        )

        i = self.sigmoid(cc_i)

        f = self.sigmoid(cc_f)

        c_next = f * c_cur + i * torch.tanh(cc_c)

        o = self.sigmoid(cc_o)

        h_next = o * torch.tanh(c_next)

        return h_next, c_next

    def init_hidden(
        self,
        batch_size,
        image_size
    ):

        height, width = image_size

        return (

            torch.zeros(

                batch_size,

                self.hidden_dim,

                height,

                width,

                device=self.conv.weight.device
            ),

            torch.zeros(

                batch_size,

                self.hidden_dim,

                height,

                width,

                device=self.conv.weight.device
            )
        )


# =====================================================
# CONV LSTM
# =====================================================

class ConvLSTM(nn.Module):

    def __init__(
        self,
        input_dim,
        hidden_dim,
        kernel_size,
        num_layers,
        batch_first=False,
        bias=True,
        return_all_layers=False
    ):

        super(ConvLSTM, self).__init__()

        self._check_kernel_size_consistency(
            kernel_size
        )

        kernel_size = self._extend_for_multilayer(
            kernel_size,
            num_layers
        )

        hidden_dim = self._extend_for_multilayer(
            hidden_dim,
            num_layers
        )

        if not len(kernel_size) == len(hidden_dim) == num_layers:

            raise ValueError(
                "Inconsistent list length."
            )

        self.input_dim = input_dim

        self.hidden_dim = hidden_dim

        self.kernel_size = kernel_size

        self.num_layers = num_layers

        self.batch_first = batch_first

        self.bias = bias

        self.return_all_layers = return_all_layers

        cell_list = []

        for i in range(0, self.num_layers):

            cur_input_dim = (

                self.input_dim

                if i == 0

                else self.hidden_dim[i - 1]
            )

            cell_list.append(

                ConvLSTMCell(

                    input_dim=cur_input_dim,

                    hidden_dim=self.hidden_dim[i],

                    kernel_size=self.kernel_size[i],

                    bias=self.bias
                )
            )

        self.cell_list = nn.ModuleList(
            cell_list
        )

    def forward(
        self,
        input_tensor,
        hidden_state=None
    ):

        if not self.batch_first:

            input_tensor = input_tensor.transpose(
                0,
                1
            )

        b, _, _, h, w = input_tensor.size()

        if hidden_state is not None:

            raise NotImplementedError()

        else:

            hidden_state = self._init_hidden(

                batch_size=b,

                image_size=(h, w)
            )

        layer_output_list = []

        last_state_list = []

        seq_len = input_tensor.size(1)

        cur_layer_input = input_tensor

        for layer_idx in range(self.num_layers):

            h, c = hidden_state[layer_idx]

            output_inner = []

            for t in range(seq_len):

                h, c = self.cell_list[layer_idx](

                    input_tensor=cur_layer_input[:, t, :, :, :],

                    cur_state=[h, c]
                )

                output_inner.append(h)

            layer_output = torch.stack(

                output_inner,

                dim=1
            )

            cur_layer_input = layer_output

            layer_output_list.append(
                layer_output
            )

            last_state_list.append(
                [h, c]
            )

        if not self.return_all_layers:

            layer_output_list = layer_output_list[-1:]

            last_state_list = last_state_list[-1:]

        return layer_output_list, last_state_list

    def _init_hidden(
        self,
        batch_size,
        image_size
    ):

        init_states = []

        for i in range(self.num_layers):

            init_states.append(

                self.cell_list[i].init_hidden(

                    batch_size,

                    image_size
                )
            )

        return init_states

    @staticmethod
    def _check_kernel_size_consistency(
        kernel_size
    ):

        if not (

            isinstance(kernel_size, tuple)

            or

            (
                isinstance(kernel_size, list)

                and

                all([
                    isinstance(elem, tuple)
                    for elem in kernel_size
                ])
            )
        ):

            raise ValueError(
                "`kernel_size` must be tuple or list of tuples"
            )

    @staticmethod
    def _extend_for_multilayer(
        param,
        num_layers
    ):

        if not isinstance(param, list):

            param = [param] * num_layers

        return param


# =====================================================
# CONV GRU CELL
# =====================================================

class ConvGruCell(nn.Module):

    def __init__(
        self,
        input_dim,
        hidden_dim,
        kernel_size,
        bias
    ):

        super(ConvGruCell, self).__init__()

        self.input_dim = input_dim

        self.hidden_dim = hidden_dim

        self.kernel_size = kernel_size

        self.padding = (
            kernel_size[0] // 2,
            kernel_size[1] // 2
        )

        self.bias = bias

        self.sigmoid = hardsigmoid

        self.conv1 = nn.Conv2d(

            in_channels=self.input_dim + self.hidden_dim,

            out_channels=2 * self.hidden_dim,

            kernel_size=self.kernel_size,

            padding=self.padding,

            bias=self.bias
        )

        self.conv2 = nn.Conv2d(

            in_channels=self.input_dim + self.hidden_dim,

            out_channels=self.hidden_dim,

            kernel_size=self.kernel_size,

            padding=self.padding,

            bias=self.bias
        )

    def forward(
        self,
        input_tensor,
        cur_state
    ):

        h_cur = cur_state

        h_x = torch.cat(

            [h_cur, input_tensor],

            dim=1
        )

        combined_conv = self.conv1(
            h_x
        )

        cc_r, cc_u = torch.split(

            combined_conv,

            self.hidden_dim,

            dim=1
        )

        r = self.sigmoid(cc_r)

        u = self.sigmoid(cc_u)

        x_r_o_h = torch.cat(

            [input_tensor, r * h_cur],

            dim=1
        )

        combined_conv = self.conv2(
            x_r_o_h
        )

        c = nn.Tanh()(combined_conv)

        h_next = (1 - u) * h_cur + u * c

        return h_next

    def init_hidden(
        self,
        batch_size,
        image_size
    ):

        height, width = image_size

        return torch.zeros(

            batch_size,

            self.hidden_dim,

            height,

            width,

            device=self.conv1.weight.device
        )


# =====================================================
# CONV GRU
# =====================================================

class ConvGRU(nn.Module):

    def __init__(
        self,
        input_dim,
        hidden_dim,
        kernel_size,
        num_layers,
        batch_first=False,
        bias=True,
        return_all_layers=False
    ):

        super(ConvGRU, self).__init__()

        self._check_kernel_size_consistency(
            kernel_size
        )

        kernel_size = self._extend_for_multilayer(
            kernel_size,
            num_layers
        )

        hidden_dim = self._extend_for_multilayer(
            hidden_dim,
            num_layers
        )

        if not len(kernel_size) == len(hidden_dim) == num_layers:

            raise ValueError(
                "Inconsistent list length."
            )

        self.input_dim = input_dim

        self.hidden_dim = hidden_dim

        self.kernel_size = kernel_size

        self.num_layers = num_layers

        self.batch_first = batch_first

        self.bias = bias

        self.return_all_layers = return_all_layers

        cell_list = []

        for i in range(0, self.num_layers):

            cur_input_dim = (

                self.input_dim

                if i == 0

                else self.hidden_dim[i - 1]
            )

            cell_list.append(

                ConvGruCell(

                    input_dim=cur_input_dim,

                    hidden_dim=self.hidden_dim[i],

                    kernel_size=self.kernel_size[i],

                    bias=self.bias
                )
            )

        self.cell_list = nn.ModuleList(
            cell_list
        )

    def forward(
        self,
        input_tensor,
        hidden_state=None
    ):

        if not self.batch_first:

            input_tensor = input_tensor.transpose(
                0,
                1
            )

        b, _, _, h, w = input_tensor.size()

        if hidden_state is not None:

            raise NotImplementedError()

        else:

            hidden_state = self._init_hidden(

                batch_size=b,

                image_size=(h, w)
            )

        layer_output_list = []

        last_state_list = []

        seq_len = input_tensor.size(1)

        cur_layer_input = input_tensor

        for layer_idx in range(self.num_layers):

            h = hidden_state[layer_idx]

            output_inner = []

            for t in range(seq_len):

                h = self.cell_list[layer_idx](

                    input_tensor=cur_layer_input[:, t, :, :, :],

                    cur_state=h
                )

                output_inner.append(h)

            layer_output = torch.stack(

                output_inner,

                dim=1
            )

            cur_layer_input = layer_output

            layer_output_list.append(
                layer_output
            )

            last_state_list.append(
                h
            )

        if not self.return_all_layers:

            layer_output_list = layer_output_list[-1:]

            last_state_list = last_state_list[-1:]

        return layer_output_list, last_state_list

    def _init_hidden(
        self,
        batch_size,
        image_size
    ):

        init_states = []

        for i in range(self.num_layers):

            init_states.append(

                self.cell_list[i].init_hidden(

                    batch_size,

                    image_size
                )
            )

        return init_states

    @staticmethod
    def _check_kernel_size_consistency(
        kernel_size
    ):

        if not (

            isinstance(kernel_size, tuple)

            or

            (
                isinstance(kernel_size, list)

                and

                all([
                    isinstance(elem, tuple)
                    for elem in kernel_size
                ])
            )
        ):

            raise ValueError(
                "`kernel_size` must be tuple or list of tuples"
            )

    @staticmethod
    def _extend_for_multilayer(
        param,
        num_layers
    ):

        if not isinstance(param, list):

            param = [param] * num_layers

        return param


# =====================================================
# REFLECT
# =====================================================

def reflect(
    x,
    minx,
    maxx
):

    rng = maxx - minx

    double_rng = 2 * rng

    mod = np.fmod(
        x - minx,
        double_rng
    )

    normed_mod = np.where(

        mod < 0,

        mod + double_rng,

        mod
    )

    out = np.where(

        normed_mod >= rng,

        double_rng - normed_mod,

        normed_mod
    ) + minx

    return np.array(
        out,
        dtype=x.dtype
    )


# =====================================================
# SYMMETRIC PAD
# =====================================================

def symm_pad(
    im,
    padding
):

    h, w = im.shape[-2:]

    left, right, top, bottom = padding

    x_idx = np.arange(
        -left,
        w + right
    )

    y_idx = np.arange(
        -top,
        h + bottom
    )

    x_pad = reflect(
        x_idx,
        -0.5,
        w - 0.5
    )

    y_pad = reflect(
        y_idx,
        -0.5,
        h - 0.5
    )

    xx, yy = np.meshgrid(
        x_pad,
        y_pad
    )

    return im[..., yy, xx]


# =====================================================
# BATCH NORM
# =====================================================

def batch_norm(
    X,
    eps=0.001
):

    N, C, H, W = X.shape

    device = X.device

    mean = X.mean(
        axis=(0, 2, 3)
    ).to(device)

    variance = (

        (
            X -

            mean.view((1, C, 1, 1))
        ) ** 2

    ).mean(axis=(0, 2, 3)).to(device)

    X = (

        X -

        mean.reshape((1, C, 1, 1))

    ) * 1.0 / torch.pow(

        (
            variance.view((1, C, 1, 1))
            + eps
        ),

        0.5
    )

    return X.to(device)