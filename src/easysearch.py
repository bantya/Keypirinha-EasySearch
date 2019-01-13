import re
import keypirinha as kp
import keypirinha_util as kpu

class EasySearch(kp.Plugin):
    SECTION_ENGINE = 'engines'

    SECTION_MAIN = 'main'

    REGEX_INPUT = r'(\S+)\s(.+)'

    REGEX_ENGINES = r'(\S+)\s(.+)'

    ITEM_EASYSEARCH = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()

    def on_start(self):
        self._load_settings()
        self._gather_engines()

        actions = []

        actions.append(self._set_action('copy', 'Copy Link', 'Copy the URL to the clipboard'))
        actions.append(self._set_action('open', 'Open', 'Open the URL in the browser'))
        actions.append(self._set_action('new', 'New window', 'Open the URL in new browser window'))
        actions.append(self._set_action('private', 'Private mode', 'Open the URL in the private mode'))

        self.set_actions(self.ITEM_EASYSEARCH, actions)

    def on_catalog(self):
        self.on_start()

    def on_suggest(self, user_input, items_chain):
        input = re.search(self.REGEX_INPUT, user_input)
        suggestions = []

        if input is None:
            return None

        for engine in self.engines:
            if engine == input.group(1):
                setting = self.settings.get_stripped(engine, self.SECTION_ENGINE)
                url = re.search(self.REGEX_ENGINES, setting)

                if len(url.groups()) == 2:
                    name, target = url.groups()
                    term = input.group(2)
                    name = name.strip().replace("_", " ")
                    target = target.strip().format(q=term.strip())

                    suggestions.append(self._set_suggestion(self._create_label(engine, name, term), target))

                    split = target.split('://')

                    if split[0] == 'http':
                        target = 'https://' + split[1]
                        suggestions.append(self._set_suggestion(self._create_label(engine, name, term), target))

                    self.set_suggestions(suggestions, kp.Match.FUZZY, kp.Sort.TARGET_ASC)

    def on_execute(self, item, action):
        if item.category() != self.ITEM_EASYSEARCH:
            return

        target = item.target()
        private_mode = self.settings.get_bool('private_mode', self.SECTION_MAIN, False)
        new_window = self.settings.get_bool('new_window', self.SECTION_MAIN, False)

        if action and action.name() == "copy":
            kpu.set_clipboard(target)
        elif action and action.name() == "private":
            self._open_browser(target, True, new_window)
        elif action and action.name() == "new":
            self._open_browser(target, private_mode, True)
        else:
            self._open_browser(target, private_mode, new_window)

    def _open_browser(self, target, private_mode, new_window):
        kpu.web_browser_command(
            private_mode = private_mode,
            new_window = new_window,
            url = target,
            execute = True
        )

    def _create_label(self, engine, name, term):
        return engine + ' : Search ' + name + ' for ' + term

    def _set_suggestion(self, label, target):
        return self.create_item(
            category = self.ITEM_EASYSEARCH,
            label = label,
            short_desc = target,
            target = target,
            args_hint = kp.ItemArgsHint.FORBIDDEN,
            hit_hint = kp.ItemHitHint.IGNORE,
            loop_on_suggest = True
        )

    def _set_error(self, msg):
        return [
            self.create_error_item(
                label = "Error",
                short_desc = msg,
                target = error
            )
        ]

    def _set_action(self, name, label, desc):
        return self.create_action(
            name = name,
            label = label,
            short_desc = desc
        )

    def _load_settings(self):
        self.settings = self.load_settings()

    def _gather_engines(self):
        self.engines = self.settings.keys(self.SECTION_ENGINE)

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self.on_start()
