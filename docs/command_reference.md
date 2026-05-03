# Command Reference

## Wake words

| Language | Wake word |
|---|---|
| RU | `компьютер`, `ассистент` |
| EN | `computer`, `assistant` |

Example: `"компьютер, открой браузер"` → opens browser.

---

## Media

| RU | EN | Gesture | Action |
|---|---|---|---|
| пауза / продолжить | pause / play | open palm | Play/Pause |
| следующий трек | next track | swipe right | Next track |
| предыдущий трек | previous track | swipe left | Previous track |

---

## Volume

| RU | EN | Gesture | Action |
|---|---|---|---|
| громче | louder / volume up | hand up | +5% |
| тише | quieter / volume down | hand down | -5% |
| звук 30 | volume 30 | — | Set to 30% |
| выключи звук | mute | fist | Mute |
| включи звук | unmute | — | Unmute |

---

## Browser

| RU | EN | Action |
|---|---|---|
| открой браузер | open browser | Launch Chrome/Edge |
| новая вкладка | new tab | Ctrl+T |
| закрой вкладку | close tab | Ctrl+W |
| следующая вкладка | next tab | Ctrl+Tab |
| предыдущая вкладка | previous tab | Ctrl+Shift+Tab |
| назад | back | Alt+Left |
| вперёд | forward | Alt+Right |
| обнови | refresh | Ctrl+R |
| найди {query} | search {query} | Ctrl+L → type → Enter |

---

## Window management

| RU | EN | Action |
|---|---|---|
| следующее окно | next window | Alt+Tab |
| предыдущее окно | previous window | Alt+Shift+Tab |
| покажи окна | show windows | Win+Tab |
| перейди в браузер | go to browser | Activate browser window |
| перейди в терминал | go to terminal | Activate terminal window |
| перейди в редактор | go to editor | Activate IDE window |

---

## Clipboard

| RU | EN | Action |
|---|---|---|
| скопируй | copy | Ctrl+C |
| вырежи | cut | Ctrl+X |
| вставь | paste | Ctrl+V |
| очисти буфер | clear clipboard | Clear clipboard |
| прочитай буфер | read clipboard | Show clipboard summary |

> Clipboard content is **never logged** by default.

---

## Terminal / Shell

| RU | EN | Risk | Action |
|---|---|---|---|
| очисти терминал | clear terminal | safe | `cls` |
| останови процесс | stop process | safe | Ctrl+C |
| последняя команда | last command | safe | Up arrow |
| вставь команду {cmd} | insert command {cmd} | medium | Type without executing |
| выполни команду {cmd} | execute command {cmd} | **dangerous** | Run with confirmation |

---

## Gesture commands

| Gesture | Intent | Safe standalone? |
|---|---|---|
| Open palm | media.play_pause | Yes |
| Fist | action.cancel | Yes |
| Swipe left | media.previous | Yes |
| Swipe right | media.next | Yes |
| Hand up | volume.up | Yes |
| Hand down | volume.down | Yes |
| Pinch | action.click | No (needs voice) |
| Two fingers | action.scroll_mode | No (needs voice) |

---

## Macros

Built-in macros (edit `config/macros.yaml` to customize):

| RU | EN | Steps |
|---|---|---|
| начать работу / рабочий режим | start work / work mode | Open Chrome + calendar + terminal |
| включи музыку | start music | Open Spotify + play |
| сделай скриншот | take screenshot | Win+Shift+S |
