qslider_stylesheet = """
QSlider::groove:horizontal {
border: 1px solid #777;
height: 10px;
border-radius: 2px;
}

QSlider::sub-page:horizontal {
background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,  stop: 0 #aaf, stop: 1 #88f);
border: 1px solid #777;
height: 10px;
border-radius: 3px;
}

QSlider::add-page:horizontal {
background: #fff;
border: 1px solid #666;
height: 10px;
border-radius: 3px;
}

QSlider::handle:horizontal {
background: #dfdfdf;
border: 1px solid #666;
width: 15px;
margin-top: -3px;
margin-bottom: -3px;
border-radius: 6px;
}
"""