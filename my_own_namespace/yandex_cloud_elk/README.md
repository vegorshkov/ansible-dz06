# my_own_namespace.yandex_cloud_elk

Коллекция Ansible для управления файлами на удалённых хостах.

## Состав коллекции

### Модули
- `my_own_module` - Создаёт файл на удалённом хосте с указанным содержимым.
  Параметры:
  - `path` (обязательный) - путь к файлу
  - `content` (обязательный) - содержимое файла

### Роли
- `my_own_role` - Роль, использующая my_own_module для создания файлов.
  Переменные:
  - `file_path` - путь к файлу (по умолчанию: /tmp/role_default.txt)
  - `file_content` - содержимое файла (по умолчанию: "Default content from role")

## Установка

В терминале bash выполнить команду:  
```
ansible-galaxy collection install my_own_namespace.yandex_cloud_elk
```

Или установка из локального архива:
```
ansible-galaxy collection install my_own_namespace-yandex_cloud_elk-1.0.0.tar.gz
```

Использование модуля (прописываем модуль в ansible):
```
- name: Create file with module
  my_own_namespace.yandex_cloud_elk.my_own_module:
    path: /tmp/test.txt
    content: "Hello World"
```


Использование роли:
```
- name: Use role from collection
  hosts: all
  roles:
    - my_own_namespace.yandex_cloud_elk.my_own_role
  vars:
    file_path: /tmp/role_test.txt
    file_content: "Content from role"
```

Лицензия:
GPL-3.0-or-later

Лицензия GNU GPL (General Public License) полностью правомерна в России, соответствуя Гражданскому кодексу РФ об открытых лицензиях. Она разрешает свободное использование, изучение, модификацию и распространение ПО, включая коммерческие цели. Главное условие — сохранение открытости исходного кода.

