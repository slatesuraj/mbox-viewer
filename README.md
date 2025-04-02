# MBOX Viewer

A lightweight web-based tool to view and search emails from MBOX files exported from Google or other email clients.

## Features

- 📂 View emails from MBOX files
- 🔍 Search emails by subject or sender
- 📅 Filter by date range
- 📧 View full email content in modal
- 📄 Paginated browsing
- ⚡ Fast and lightweight (Python standard library only)

## Requirements

- Python 3.6+
- Modern web browser

## Installation & Usage

1. **Place your MBOX file** in the project directory (default looks for `emails.mbox`)
2. **Run the server**:
   ```bash
   python3 mbox_viewer.py
   ```
3. **Open in browser**:
   ```
   http://localhost:8000
   ```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-p PORT` | Port to run server on | 8000 |
| `-f FILE` | Path to MBOX file | emails.mbox |

Example:
```bash
python3 mbox_viewer.py -p 8080 -f /path/to/your.mbox
```

## API Endpoints

| Endpoint | Description | Parameters |
|----------|-------------|------------|
| `/` | Serves the HTML interface | - |
| `/emails` | Returns paginated email list | `page`, `per_page`, `search`, `sender`, `from_date`, `to_date` |
| `/email` | Returns single email by ID | `id` |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `/` | Focus search box |
| `Esc` | Close email modal |
| `→` | Next page |
| `←` | Previous page |

## Troubleshooting

**Common Issues:**

1. **No emails found**
   - Verify your MBOX file exists in the correct location
   - Check the file contains valid email messages
   - Try with the sample `emails.mbox` first

2. **JSON parsing errors**
   - Stop and restart the server
   - Check browser console for detailed errors
   - Try a hard refresh (Ctrl+F5)

3. **Server not starting**
   - Verify Python 3.6+ is installed
   - Check no other service is using port 8000

## Development

To modify the tool:

1. Edit `mbox_viewer.py` for backend changes
2. Edit `app.js` for frontend logic
3. Edit `styles.css` for visual changes
4. The server auto-reloads when Python files change

## Limitations

- Only supports standard MBOX format
- Large files (>1GB) may take time to load
- Limited to Python standard library modules

## License

Apache2.0
s
## Support

For issues or feature requests, please open an issue on GitHub.
