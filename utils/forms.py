def get_form_error(form, default_error_message):
    error_message = default_error_message

    for field_name, error_messages in form.errors.items():
        for err in error_messages:
            error_message = err
            break

        if error_message is not default_error_message:
            break

    return error_message
