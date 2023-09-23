from dcspy.models import ControlKeyData


def get_input_request_for_input(ctrl_input: ControlKeyData) -> str:
    """
    Generate request string for control input.

    :param ctrl_input: ControlKeyData instance
    :return: request
    """
    request = str(ctrl_input)

    return request
