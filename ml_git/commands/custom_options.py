"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from click import Option, UsageError, MissingParameter


class MutuallyExclusiveOption(Option):
    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        help = kwargs.get('help', '')
        if self.mutually_exclusive:
            ex_str = ', '.join(self.mutually_exclusive)
            kwargs['help'] = help + (
                    ' NOTE: Mutually exclusive with'
                    ' argument: ' + ex_str + '.'
            )
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            raise UsageError(
                'The argument `{}` is mutually exclusive with '
                'argument `{}`.'.format(
                    self.name,
                    ', '.join(self.mutually_exclusive)
                )
            )

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx,
            opts,
            args
        )


class OptionRequiredIf(Option):
    def __init__(self, *args, **kwargs):
        self.required_option = set(kwargs.pop('required_option', []))
        help = kwargs.get('help', '')
        if self.required_option:
            ex_str = ', '.join(self.required_option)
            kwargs['help'] = help + (' NOTE: This option is required if --' + ex_str + ' is used.')
        super(OptionRequiredIf, self).__init__(*args, **kwargs)

    def full_process_value(self, ctx, value):
        value = super(OptionRequiredIf, self).full_process_value(ctx, value)

        ex_str = ', '.join(self.required_option)
        ex_str = ex_str.replace("-", "_")
        if value is None and ctx.params[ex_str] is not None:
            msg = 'The argument `{}` is required if `{}` is used.'.format(
                self.name,
                ', '.join(self.required_option)
            )
            raise MissingParameter(ctx=ctx, param=self, message=msg)
        return value
