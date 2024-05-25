## Вопрос
Какие пользователи подключенные к VPN в настоящий момент?
## Ответ
Запрос в SIEM
```
| inputlookup lookup1
| search type=vpn AND end_time=0
```
