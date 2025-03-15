# GTK 4.0 Development Guide for Preview Maker

## Overview
This guide provides essential information about GTK 4.0 development specifically for the Preview Maker application. It covers key concepts, patterns, and resources to help both human developers and AI assistants work effectively with GTK 4.0 in this project.

## GTK 4.0 Basics

### Key Concepts
1. **Widget Hierarchy**: GTK uses a hierarchical widget structure where containers hold other widgets
2. **Signal System**: Widgets emit signals that can be connected to callback functions
3. **GObject Properties**: Widgets have properties that can be set and retrieved
4. **CSS Styling**: Widgets can be styled using CSS

### Core GTK 4.0 Changes from GTK 3
1. **Event Model**: Completely revamped event handling system
2. **Rendering**: Uses GPU-accelerated rendering by default
3. **Gestures**: New gesture handling system replaces event signals
4. **Drag and Drop**: Redesigned API for drag and drop operations
5. **Layouts**: New layout system with constraints

## Key GTK 4.0 Components Used in Preview Maker

### Windows and Containers
- `Gtk.ApplicationWindow`: Main application window
- `Gtk.Box`: Arranges widgets horizontally or vertically
- `Gtk.Grid`: Arranges widgets in a grid
- `Gtk.Paned`: Divides space between two widgets with adjustable separator
- `Gtk.ScrolledWindow`: Adds scrollbars to contained widgets

### UI Components
- `Gtk.Button`: Clickable button
- `Gtk.Label`: Text display
- `Gtk.Image`: Image display
- `Gtk.Entry`: Single line text entry
- `Gtk.Switch`: On/off toggle
- `Gtk.ProgressBar`: Progress indicator
- `Gtk.InfoBar`: Information notification bar

### Dialogs and Popups
- `Gtk.Dialog`: Modal dialog window
- `Gtk.FileChooserDialog`: File selection dialog
- `Gtk.MessageDialog`: Simple message dialog
- `Gtk.Popover`: Pop-up that's attached to a widget

### Advanced Components
- `Gtk.DropTarget`: For handling drag and drop operations
- `Gtk.GestureClick`: For handling click events
- `Gtk.DrawingArea`: For custom drawing (used for image preview)
- `Gtk.Overlay`: For overlaying widgets (used for zoom preview)

## Common GTK 4.0 Patterns

### Application Structure
```python
class MyApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.myapp",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        # Configure window
        window.present()
```

### Signal Connections
```python
# Connect a button click to a function
button = Gtk.Button(label="Click Me")
button.connect("clicked", self.on_button_clicked)

def on_button_clicked(self, button):
    print("Button was clicked")
```

### Widget Properties
```python
# Setting properties
label = Gtk.Label(label="Hello", halign=Gtk.Align.CENTER)

# Getting properties
text = label.get_text()
```

### Drag and Drop Support
```python
# Set up drag source
drag_source = Gtk.DragSource()
drag_source.set_actions(Gdk.DragAction.COPY)
drag_source.connect("prepare", self.on_drag_prepare)
widget.add_controller(drag_source)

# Set up drop target
drop_target = Gtk.DropTarget()
drop_target.set_gtypes([Gdk.FileList])
drop_target.connect("drop", self.on_drop)
widget.add_controller(drop_target)
```

### Custom Drawing
```python
drawing_area = Gtk.DrawingArea()
drawing_area.set_draw_func(self.draw_function)

def draw_function(self, area, cr, width, height):
    # Cairo drawing code here
    cr.set_source_rgb(0.5, 0.5, 0.5)
    cr.rectangle(0, 0, width, height)
    cr.fill()
```

## Preview Maker-Specific GTK Patterns

### Image Loading and Display
```python
def load_image(self, file_path):
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
    self.image.set_from_pixbuf(pixbuf)
```

### Circular Overlay Drawing
```python
def draw_circular_overlay(self, cr, x, y, radius, zoom_center_x, zoom_center_y):
    # Save context
    cr.save()

    # Draw the full image
    cr.set_source_surface(self.image_surface, 0, 0)
    cr.paint()

    # Create circular path
    cr.arc(x, y, radius, 0, 2 * math.pi)

    # Create circular mask
    cr.set_source_rgba(0, 0, 0, 0.5)
    cr.set_operator(cairo.OPERATOR_OVER)
    cr.fill_preserve()

    # Draw zoomed part
    cr.set_source_surface(self.zoom_surface,
                           x - (zoom_center_x * self.zoom_factor),
                           y - (zoom_center_y * self.zoom_factor))
    cr.fill()

    # Draw circle border
    cr.set_source_rgb(1, 1, 1)
    cr.set_line_width(2)
    cr.stroke()

    # Restore context
    cr.restore()
```

### Notification System
```python
def show_notification(self, message, timeout=5):
    """Display a notification message."""
    infobar = Gtk.InfoBar()
    infobar.set_message_type(Gtk.MessageType.INFO)

    label = Gtk.Label(label=message)
    content = infobar.get_content_area()
    content.append(label)

    self.main_box.append(infobar)
    infobar.set_revealed(True)

    # Auto-hide after timeout
    GLib.timeout_add_seconds(timeout, lambda: infobar.set_revealed(False))
    GLib.timeout_add_seconds(timeout + 1, lambda: self.main_box.remove(infobar))
```

## Common GTK 4.0 Challenges and Solutions

### Challenge: Managing Large Images
**Solution:**
- Load images asynchronously to prevent UI freezing
- Scale images for display while keeping original for processing
- Use `GdkPixbufLoader` for incremental loading of large images

```python
def load_image_async(self, file_path):
    def load_in_thread():
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)
            GLib.idle_add(self.on_image_loaded, pixbuf)
        except Exception as e:
            GLib.idle_add(self.on_image_error, str(e))

    thread = threading.Thread(target=load_in_thread)
    thread.daemon = True
    thread.start()
```

### Challenge: Drag and Drop for Multiple Files
**Solution:**
- Use `Gdk.FileList` for handling multiple files
- Process files sequentially or in batches

```python
def on_drop(self, drop_target, value, x, y):
    if isinstance(value, Gdk.FileList):
        files = value.get_files()
        for file in files:
            file_path = file.get_path()
            if self.is_supported_file(file_path):
                self.process_file(file_path)
    return True
```

### Challenge: Custom Drawing Performance
**Solution:**
- Cache surfaces when possible
- Redraw only when necessary
- Use optimal drawing operations

```python
def update_drawing_area(self):
    # Only redraw if needed
    if self.needs_redraw:
        self.drawing_area.queue_draw()
        self.needs_redraw = False
```

### Challenge: Responsive UI During Processing
**Solution:**
- Use threads for heavy processing
- Update UI from main thread using `GLib.idle_add`
- Show progress indicators

```python
def process_image_with_progress(self, image_path):
    # Start progress bar
    self.progress_bar.set_visible(True)

    def process_thread():
        # Do heavy processing here
        result = self.processor.process(image_path)

        # Update UI in main thread
        GLib.idle_add(self.on_processing_complete, result)

    thread = threading.Thread(target=process_thread)
    thread.daemon = True
    thread.start()

    # Update progress periodically
    GLib.timeout_add(100, self.update_progress)
```

## Testing GTK Applications

### Manual Testing
- Test on different screen sizes and resolutions
- Verify proper keyboard navigation
- Check theme compatibility
- Test with accessibility tools

### Automated Testing
- Use `GtkInspector` for UI debugging
- Write unit tests with `GTest`
- Create UI tests with tools like `dogtail` or custom test framework

## GTK Resources

### Official Documentation
- [GTK 4 API Reference](https://docs.gtk.org/gtk4/)
- [GTK 4 Development Blog](https://blog.gtk.org/)
- [GNOME Developer Documentation](https://developer.gnome.org/)

### Tutorials and Guides
- [GTK 4 Tutorial](https://docs.gtk.org/gtk4/getting_started.html)
- [Python GObject Introspection API](https://pygobject.readthedocs.io/en/latest/)
- [GUI Programming with Python and GTK](https://python-gtk-3-tutorial.readthedocs.io/)

### Tools
- GTK Inspector: Launch with `GTK_DEBUG=interactive` environment variable
- Glade: UI designer for GTK (Note: still transitioning to GTK 4)
- D-Feet: D-Bus debugger for GTK applications

## Conclusion
GTK 4.0 provides a powerful framework for building the Preview Maker application. By understanding the key concepts and patterns outlined in this guide, developers and AI assistants can effectively work with the GTK components used in this project. Remember to follow the established patterns for consistent code organization and optimal performance.