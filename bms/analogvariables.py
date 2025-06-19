from entities.descriptors import AnalogVariableDescriptor, AnalogAlarmDescriptor
from firmwareconfig import FirmwareConfig as fwcfg


def linear_regression(x0, y0, x1, y1, x):
    m = float((y1-y0) / (x1-x0))
    return m * (x-x0) + y0

def quadratic(a, b, c, x):
    y = a*x*x + b*x + c
    return y

def channel2voltage_ADC(_channel):
    """Convert from the ADC channel to the ADC voltage"""
    num_channels = fwcfg.ADC_NUM_CHANNELS
    voltage_reference = 4.096
    assert _channel <= (num_channels - 1), "channel2voltage_ADC _channel = {} (maximum allowed is {})".format(_channel, num_channels-1)
    assert _channel >= 0, "channel2voltage_ADC _channel = {} (minimum allowed is {})".format(_channel, 0)
    return float(_channel) * voltage_reference / num_channels


def voltage2channel_ADC(_voltage):
    """Convert from the ADC voltage to ADC channel"""
    num_channels = fwcfg.ADC_NUM_CHANNELS
    voltage_reference = 4.096
    assert _voltage <= voltage_reference, "voltage2channel_ADC _voltage = {} (maximum allowed is {})".format(_voltage, voltage_reference)
    adc_channel = round(num_channels * float(_voltage) / voltage_reference)
    return adc_channel


def convert_chn2meas_DUL_BOARDTEMP(_chn):
    # from Rocco's "mapping" doc (vers. 15.02.2021):
    # ~ 1.5V @ 25C
    # ~ 3.0V @ 100C
    v = channel2voltage_ADC(_chn)
    v0 = 1.5; meas0 = 25.; v1 = 3.0; meas1 = 100.
    return linear_regression(v0, meas0, v1, meas1, v)


def convert_chn2meas_TEMP2(_chn):
    # todo: remove
    # # OLD:
    # # from Rocco's "mapping" doc (vers. 15.02.2021):
    # # ~ 0.7V@30C
    # # ~ 3.2V@100C
    # v = channel2voltage_ADC(_chn)
    # v0 = 0.7; meas0 = 30.; v1 = 3.2; meas1 = 100.
    # return linear_regression(v0, meas0, v1, meas1, v)

    # new version with quadratic fit
    # (Rocco's mail 9/12/2021)
    #a = -15.327
    #b = 65.478
    #c = -8.819
    #v = channel2voltage_ADC(_chn)
    #return quadratic(a,b,c,v)
    a = 23.24
    b = -25.79
    v = channel2voltage_ADC(_chn)
    return linear_regression(0.0, b, 1.0, a + b, v)


def convert_chn2meas_TEMP1(_chn):
    # same as TEMP2
    return convert_chn2meas_TEMP2(_chn)


def convert_chn2meas_VEOC_RTN_I(_chn):
    # from Rocco's "mapping" doc (vers. 15.02.2021):
    # ~ 1.36V@0A
    # ~ 4.51V@3A
    v = channel2voltage_ADC(_chn)
    v0 = 1.36; meas0 = 0.; v1 = 4.51; meas1 = 3.
    return linear_regression(v0, meas0, v1, meas1, v)


def convert_chn2meas_VEOC_FWR_I(_chn):
    # from Rocco's "mapping" doc (vers. 15.02.2021):
    # same as VEOC_RTN_I
    return convert_chn2meas_VEOC_RTN_I(_chn)


def convert_chn2meas_HYDRO_I(_chn):
    # from Rocco's "mapping" doc (vers. 15.02.2021):
    # ~ 0.45V@40mA
    # ~ 4.5V@400mA
    v = channel2voltage_ADC(_chn)
    v0 = 0.45; meas0 = 0.040; v1 = 4.5; meas1 = 0.4
    return linear_regression(v0, meas0, v1, meas1, v)


def convert_chn2meas_INPUT_V(_chn):
    # from Rocco's "mapping" doc (vers. 15.02.2021):
    # ~ 1,3V@260V
    # ~ 2.0V@400V
    v = channel2voltage_ADC(_chn)
    v0 = 1.3; meas0 = 260.; v1 = 2.; meas1 = 400.
    return linear_regression(v0, meas0, v1, meas1, v)


def convert_chn2meas_LBL_I(_chn):
    # from Rocco's "mapping" doc (vers. 15.02.2021):
    # ~ 0.45V@70mA
    # ~ 4.5V@700mA
    v = channel2voltage_ADC(_chn)
    v0 = 0.45; meas0 = 0.070; v1 = 4.5; meas1 = 0.7
    return linear_regression(v0, meas0, v1, meas1, v)


def convert_chn2meas_GLRA_I(_chn):
    # from Rocco's "mapping" doc (vers. 15.02.2021):
    # ~ 3.6V@5.3A
    v = channel2voltage_ADC(_chn)
    v0 = 0.; meas0 = 0.; v1 = 3.6; meas1 = 5.3
    return linear_regression(v0, meas0, v1, meas1, v)


def convert_chn2meas_GLRB_I(_chn):
    # from Rocco's "mapping" doc (vers. 15.02.2021):
    # same as GLRA_I
    return convert_chn2meas_GLRA_I(_chn)


def convert_chn2meas_PWB_I(_chn):
    # from Rocco's "mapping" doc (vers. 15.02.2021):
    # ~ 3.6V@2.6A
    v = channel2voltage_ADC(_chn)
    v0 = 0.; meas0 = 0.; v1 = 3.6; meas1 = 2.6
    return linear_regression(v0, meas0, v1, meas1, v)


def __convert_maes2chn_invert_relation(_chn2meas, _meas):
    meas0 = _chn2meas(100)
    meas1 = _chn2meas(5000)
    return linear_regression(meas0, 100, meas1, 5000, _meas)


def convert_meas2chn_DUL_BOARDTEMP(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_DUL_BOARDTEMP, _meas)


def convert_meas2chn_TEMP2(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_TEMP2, _meas)


def convert_meas2chn_TEMP1(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_TEMP1, _meas)


def convert_meas2chn_VEOC_RTN_I(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_VEOC_RTN_I, _meas)


def convert_meas2chn_VEOC_FWR_I(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_VEOC_FWR_I, _meas)


def convert_meas2chn_HYDRO_I(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_HYDRO_I, _meas)


def convert_meas2chn_INPUT_V(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_INPUT_V, _meas)


def convert_meas2chn_LBL_I(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_LBL_I, _meas)


def convert_meas2chn_GLRA_I(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_GLRA_I, _meas)


def convert_meas2chn_GLRB_I(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_GLRB_I, _meas)


def convert_meas2chn_PWB_I(_meas):
    return __convert_maes2chn_invert_relation(convert_chn2meas_PWB_I, _meas)


class AnalogVariableList:
    """A class to define the list of analog variables of the BPS"""

    # this class can be actually created only once
    _ready = False

    def __init__(self, _var_enum_index_start, _alarm_enum_index_start):
        assert self._ready is False, "Class {} should be created only once!".format(self.__class__.__name__)
        self._create(_var_enum_index_start, _alarm_enum_index_start)
        self._ready = True

    def count(self):
        return len(self.vars)

    def entries(self):
        return self.vars

    def get_var_enum_indexes(self):
        return [var.enum_index for var in self.vars]

    def get_alarm_enum_indexes(self):
        alarm_enum_indexes = []
        for var in self.vars:
            if var.alarm_slow:
                alarm_enum_indexes.append(var.alarm_slow.enum_index)
            if var.alarm_fast:
                alarm_enum_indexes.append(var.alarm_fast.enum_index)
        return alarm_enum_indexes

    def _create(self, _var_enum_index_start, _alarm_enum_index_start):
        self.vars = list()

        alarm_enum_index = _alarm_enum_index_start
        var_enum_index = _var_enum_index_start


        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_DUL_BOARDTEMP',
                analog_channel=0,
                channel2measure_converter=convert_chn2meas_DUL_BOARDTEMP,
                measure2channel_converter=convert_meas2chn_DUL_BOARDTEMP,
                description='DUL board temperature sensor',
                units='C',
                enum_index=var_enum_index,
                alarm_slow=None,
                alarm_fast=None
                # alarm_slow=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index,
                #     enable_default=False,
                #     threshold_default=60.,  # TODO
                #     timeout_default_ms=100.  # TODO
                # ),
                # alarm_fast=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index+1,
                #     enable_default=False,
                #     threshold_default=60.,  # TODO
                #     timeout_default_ms=100.  # TODO
                # )
            )
        )

        var_enum_index += 1
        if self.vars[-1].alarm_slow:
            alarm_enum_index += 1
        if self.vars[-1].alarm_fast:
            alarm_enum_index += 1

        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_TEMP2',
                analog_channel=1,
                channel2measure_converter=convert_chn2meas_TEMP2,
                measure2channel_converter=convert_meas2chn_TEMP2,
                description='VICOR2 Heatsink (connector J12) temperature sensor signal acquisition',
                units='C',
                enum_index=var_enum_index,
                alarm_slow=None,
                alarm_fast=None
                # alarm_slow=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index,
                #     enable_default=False,
                #     threshold_default=60.,  # TODO
                #     timeout_default_ms=100.  # TODO
                # ),
                # alarm_fast=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index+1,
                #     enable_default=False,
                #     threshold_default=60.,  # TODO
                #     timeout_default_ms=100.  # TODO
                # )
            )
        )

        var_enum_index += 1
        if self.vars[-1].alarm_slow:
            alarm_enum_index += 1
        if self.vars[-1].alarm_fast:
            alarm_enum_index += 1

        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_TEMP1',
                analog_channel=2,
                channel2measure_converter=convert_chn2meas_TEMP1,
                measure2channel_converter=convert_meas2chn_TEMP1,
                description='VICOR1 Heatsink (connector J1) temperature sensor signal acquisition ',
                units='C',
                enum_index=var_enum_index,
                alarm_slow=None,
                alarm_fast=None
                # alarm_slow=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index,
                #     enable_default=False,
                #     threshold_default=60.,  # TODO
                #     timeout_default_ms=100.  # TODO
                # ),
                # alarm_fast=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index+1,
                #     enable_default=False,
                #     threshold_default=60.,  # TODO
                #     timeout_default_ms=100.  # TODO
                # )
            )
        )

        var_enum_index += 1
        if self.vars[-1].alarm_slow:
            alarm_enum_index += 1
        if self.vars[-1].alarm_fast:
            alarm_enum_index += 1

        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_VEOC_RTN_I',
                analog_channel=3,
                channel2measure_converter=convert_chn2meas_VEOC_RTN_I,
                measure2channel_converter=convert_meas2chn_VEOC_RTN_I,
                description='DU backbone return current sensor signal acquisition ',
                units='A',
                enum_index=var_enum_index,
                alarm_slow=AnalogAlarmDescriptor(
                    enum_index=alarm_enum_index,
                    enable_default=True,
                    threshold_default=1.5,  # TODO
                    timeout_default_ms=150.  # TODO
                ),
                alarm_fast=AnalogAlarmDescriptor(
                    enum_index=alarm_enum_index+1,
                    enable_default=True,
                    threshold_default=2.5,  # TODO
                    timeout_default_ms=35.  # TODO
                )
            )
        )

        var_enum_index += 1
        if self.vars[-1].alarm_slow:
            alarm_enum_index += 1
        if self.vars[-1].alarm_fast:
            alarm_enum_index += 1

        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_VEOC_FWR_I',
                analog_channel=4,
                channel2measure_converter=convert_chn2meas_VEOC_FWR_I,
                measure2channel_converter=convert_meas2chn_VEOC_FWR_I,
                description='DU backbone forward current sensor signal acquisition ',
                units='A',
                enum_index=var_enum_index,
                alarm_slow=AnalogAlarmDescriptor(
                    enum_index=alarm_enum_index,
                    enable_default=True,
                    threshold_default=1.4,  # TODO
                    timeout_default_ms=150.  # TODO
                ),
                alarm_fast=AnalogAlarmDescriptor(
                    enum_index=alarm_enum_index+1,
                    enable_default=True,
                    threshold_default=2.4,  # TODO
                    timeout_default_ms=35.  # TODO
                )
            )
        )

        var_enum_index += 1
        if self.vars[-1].alarm_slow:
            alarm_enum_index += 1
        if self.vars[-1].alarm_fast:
            alarm_enum_index += 1

        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_HYDRO_I',
                analog_channel=5,
                channel2measure_converter=convert_chn2meas_HYDRO_I,
                measure2channel_converter=convert_meas2chn_HYDRO_I,
                description='HYDRO current sensor signal acquisition ',
                units='A',
                enum_index=var_enum_index,
                alarm_slow=AnalogAlarmDescriptor(
                    enum_index=alarm_enum_index,
                    enable_default=False,
                    threshold_default=0.15,  # TODO
                    timeout_default_ms=500.  # TODO
                ),
                alarm_fast=AnalogAlarmDescriptor(
                    enum_index=alarm_enum_index+1,
                    enable_default=False,
                    threshold_default=0.35,  # TODO
                    timeout_default_ms=50.  # TODO
                )
            )
        )

        var_enum_index += 1
        if self.vars[-1].alarm_slow:
            alarm_enum_index += 1
        if self.vars[-1].alarm_fast:
            alarm_enum_index += 1

        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_INPUT_V',
                analog_channel=6,
                channel2measure_converter=convert_chn2meas_INPUT_V,
                measure2channel_converter=convert_meas2chn_INPUT_V,
                description='Main Input Line voltage sensor signal acquisition ',
                units='V',
                enum_index=var_enum_index,
                alarm_slow=None,
                alarm_fast=None
                # alarm_slow=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index,
                #     enable_default=False,
                #     threshold_default=405.,  # TODO
                #     timeout_default_ms=100.  # TODO
                # ),
                # alarm_fast=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index+1,
                #     enable_default=False,
                #     threshold_default=405.,  # TODO
                #     timeout_default_ms=100.  # TODO
                # )
            )
        )

        var_enum_index += 1
        if self.vars[-1].alarm_slow:
            alarm_enum_index += 1
        if self.vars[-1].alarm_fast:
            alarm_enum_index += 1

        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_LBL_I',
                analog_channel=7,
                channel2measure_converter=convert_chn2meas_LBL_I,
                measure2channel_converter=convert_meas2chn_LBL_I,
                description='LBL current sensor signal acquisition ',
                units='A',
                enum_index=var_enum_index,
                alarm_slow=AnalogAlarmDescriptor(
                    enum_index=alarm_enum_index,
                    enable_default=False,
                    threshold_default=0.50,  # TODO
                    timeout_default_ms=500.  # TODO
                ),
                alarm_fast=AnalogAlarmDescriptor(
                    enum_index=alarm_enum_index+1,
                    enable_default=False,
                    threshold_default=0.60,  # TODO
                    timeout_default_ms=50.  # TODO
                )
            )
        )

        var_enum_index += 1
        if self.vars[-1].alarm_slow:
            alarm_enum_index += 1
        if self.vars[-1].alarm_fast:
            alarm_enum_index += 1

        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_GLRA_I',
                analog_channel=8,
                channel2measure_converter=convert_chn2meas_GLRA_I,
                measure2channel_converter=convert_meas2chn_GLRA_I,
                description='GLENAIR-A current sensor signal acquisition',
                units='A',
                enum_index=var_enum_index,
                alarm_slow=None,
                alarm_fast=None
                # alarm_slow=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index,
                #     enable_default=False,
                #     threshold_default=6.0,  # TODO
                #     timeout_default_ms=100.  # TODO
                # ),
                # alarm_fast=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index+1,
                #     enable_default=False,
                #     threshold_default=6.0,  # TODO
                #     timeout_default_ms=100.  # TODO
                # )
            )
        )

        var_enum_index += 1
        if self.vars[-1].alarm_slow:
            alarm_enum_index += 1
        if self.vars[-1].alarm_fast:
            alarm_enum_index += 1

        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_GLRB_I',
                analog_channel=9,
                channel2measure_converter=convert_chn2meas_GLRB_I,
                measure2channel_converter=convert_meas2chn_GLRB_I,
                description='GLENAIR-B current sensor signal acquisition',
                units='A',
                enum_index=var_enum_index,
                alarm_slow=None,
                alarm_fast=None
                # alarm_slow=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index,
                #     enable_default=False,
                #     threshold_default=6.0,  # TODO
                #     timeout_default_ms=100.  # TODO
                # ),
                # alarm_fast=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index+1,
                #     enable_default=False,
                #     threshold_default=6.0,  # TODO
                #     timeout_default_ms=100.  # TODO
                # )
            )
        )

        var_enum_index += 1
        if self.vars[-1].alarm_slow:
            alarm_enum_index += 1
        if self.vars[-1].alarm_fast:
            alarm_enum_index += 1

        self.vars.append(
            AnalogVariableDescriptor(
                firmware_config=fwcfg,
                name='MON_PWB_I',
                analog_channel=10,
                channel2measure_converter=convert_chn2meas_PWB_I,
                measure2channel_converter=convert_meas2chn_PWB_I,
                description='POWER BOARD current sensor signal acquisition',
                units='A',
                enum_index=var_enum_index,
                alarm_slow=None,
                alarm_fast=None
                # alarm_slow=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index,
                #     enable_default=False,
                #     threshold_default=1.8,  # TODO
                #     timeout_default_ms=100.  # TODO
                # ),
                # alarm_fast=AnalogAlarmDescriptor(
                #     enum_index=alarm_enum_index+1,
                #     enable_default=False,
                #     threshold_default=1.8,  # TODO
                #     timeout_default_ms=100.  # TODO
                # )
            )
        )

        print("Analog Variables, latest alarm index defined: ", alarm_enum_index+1)


if __name__ == '__main__':
    analog_variables = AnalogVariableList()
    print(analog_variables.vars[0].name)


