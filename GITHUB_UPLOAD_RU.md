# Публикация на GitHub

Этот архив содержит исходный код и тесты. В нём нет ваших документов, PDF-файлов, кешей Python или скомпилированного EXE.

## Через веб-интерфейс (без Git)

1. Откройте https://github.com/new и создайте репозиторий с названием `pdf-compressor`.
2. Для первого размещения рекомендуется **Private**, чтобы проверить код и выбрать лицензию. Позже можно сменить видимость на Public.
3. Репозиторий создайте без галочек **Add a README file**, **Add .gitignore** и **Choose a license** — нужные файлы уже подготовлены (лицензия проекта пока должна быть согласована отдельно).
4. Откройте **Add file → Upload files**.
5. Перетащите **содержимое папки `PDF-Compressor-GitHub`**, включая `.github`, `tests` и файлы README. Если веб-интерфейс не позволяет добавить скрытые папки, загрузите код через Git (ниже).
6. Нажмите **Commit changes**.

## Через скрипт (рекомендуется)

Установите Git for Windows, создайте пустой репозиторий на GitHub, затем запустите `Publish_to_GitHub.bat`. Вставьте HTTPS-ссылку нового репозитория, например `https://github.com/USERNAME/pdf-compressor.git`. При необходимости Git предложит войти через браузер.

## Через Git вручную (альтернатива)

Установите Git for Windows, создайте пустой репозиторий на GitHub, затем откройте CMD/PowerShell в этой папке:

```powershell
git init
git add .
git commit -m "Initial release: PDF Compressor 2.6"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/pdf-compressor.git
git push -u origin main
```

Замените `YOUR_USERNAME` на ваш GitHub-логин. При первом push Git может предложить вход через браузер. **Не отправляйте никому личные токены или пароли.**

После публикации на GitHub откройте **Settings → General → Description** и добавьте: `Offline bilingual PDF compressor for Windows (Python, PySide6, PyMuPDF)`.

Теги: `pdf`, `pdf-compressor`, `python`, `pyside6`, `desktop-app`, `windows`, `offline`, `pdf-tools`.

**Перед переключением репозитория в Public** определитесь с лицензией исходного кода и проверьте требования AGPL PyMuPDF.
