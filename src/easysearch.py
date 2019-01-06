# Keypirinha: a fast launcher for Windows (keypirinha.com)

import re
import keypirinha as kp
import keypirinha_util as kpu

class EasySearch(kp.Plugin):

    SECTION = 'engines'

    # g indian people
    REGEX_INPUT = r'(\S+)\s(.+)'

    # Google https://www.google.com/search?q=%s
    REGEX_ENGINES = r'(\S+)\s(.+)'

    ITEM_CAT = kp.ItemCategory.URL

    def __init__(self):
        super().__init__()
        self._debug = True

    def on_start(self):
        self._gather_engines()

    def on_catalog(self):
        self.on_start()

    def on_suggest(self, user_input, items_chain):
        # urllib.parse.quote_plus(search_terms))
        input = re.search(self.REGEX_INPUT, user_input)

        if input is None:
            return None

        for engine in self.engines:
            if engine == input.group(1):
                setting = self._get_setting(engine)
                url = re.search(self.REGEX_ENGINES, setting)

                if len(url.groups()) == 2:
                    name, link = url.groups()
                    term = input.group(2)
                    target = link
                    link = link.replace("%s", term)
                    target = target.replace("%s", term.strip())

                    suggestion = self._set_suggestion(link, target, name)
                    self.set_suggestions(suggestion)

    def _set_suggestion(self, corrected_url, target, name):
        return [
            self.create_item(
                category=self.ITEM_CAT,
                label=corrected_url,
                short_desc=target,
                target=target,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE
            )
        ]

    def _set_error(self, msg):
        return [
            self.create_error_item(
                label="Error",
                short_desc=msg,
                target=error
            )
        ]

    def on_execute(self, item, action):
        if item.category() != self.ITEM_CAT:
            return

        # kpu.execute_default_action(self, item, action)
        kpu.web_browser_command(
            private_mode=False,
            new_window=False,
            url=item.target(),
            execute=True
        )

    def _gather_engines(self):
        self.engines = self.load_settings().keys(self.SECTION)

    def _get_setting(self, setting):
        return self.load_settings().get_stripped(
            setting,
            section=self.SECTION,
            fallback=self.SECTION)

    # def on_events(self, flags):
    #     if flags & kp.Events.PACKCONFIG:
    #         self.on_start()

    def _get_link(self, user_input):
        pass
