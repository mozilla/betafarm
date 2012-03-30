from mock import Mock, patch

from innovate.utils import ImageStorage


@patch('innovate.utils.Image')
def _save_image(Image, name='test_photo.png', format='PNG', mode='RGB'):
    """Mock for file."""
    mock_image = Mock()
    mock_image.name = name
    mock_image.format = format
    mock_image.mode = mode

    Image.open.return_value = mock_image
    Image.ANTIALIAS = 1
    s = ImageStorage()
    s._save(mock_image.name, None)

    return mock_image
