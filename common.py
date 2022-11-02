

def check_args_exist(args, actions, required_args):
    options = {action.dest: action.option_strings[0]
               for action in actions}

    errors = []
    for arg_name in required_args:
        if not args.__dict__[arg_name]:
            errors.append(options[arg_name])
    if errors:
        raise ValueError(f"Missing required parameters: {', '.join(errors)}")

