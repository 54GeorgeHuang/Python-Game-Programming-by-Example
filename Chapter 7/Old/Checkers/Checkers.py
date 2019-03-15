import threading
import wx

import CheckersModel
import WxUtils


class Checkers(wx.Frame):


    def __init__(self, checkersModel, title='Checkers'):

        self._checkersModel = checkersModel

        style = wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.CAPTION | \
                wx.SYSTEM_MENU | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, title=title, style=style)
        self.SetBackgroundColour(wx.Colour(232, 232, 232))
        
        self.Bind(wx.EVT_CLOSE, self._onCloseWindow)
        
        quitCommandID = wx.NewId()
        self.Bind(wx.EVT_MENU, self._onQuitCommand,
                  id=quitCommandID)
        acceleratorTable = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE,
             quitCommandID)
        ])
        self.SetAcceleratorTable(acceleratorTable)
        
        self._sceneStaticBitmap = wx.StaticBitmap(self)
        self._boardStaticBitmap = wx.StaticBitmap(self)
        self._showImages()
        
        videosSizer = wx.BoxSizer(wx.HORIZONTAL)
        videosSizer.Add(self._sceneStaticBitmap)
        videosSizer.Add(self._boardStaticBitmap)

        rotateBoardButton = wx.Button(
                self, label='Rotate board CCW')
        rotateBoardButton.Bind(
                wx.EVT_BUTTON,
                self._onRotateBoardClicked)

        flipBoardXButton = wx.Button(
                self, label='Flip board X')
        flipBoardXButton.Bind(
                wx.EVT_BUTTON,
                self._onFlipBoardXClicked)

        flipBoardYButton = wx.Button(
                self, label='Flip board Y')
        flipBoardYButton.Bind(
                wx.EVT_BUTTON,
                self._onFlipBoardYClicked)

        shadowDirectionRadioBox = wx.RadioBox(
                self, label='Shadow direction',
                choices=['up', 'left', 'down', 'right'])
        shadowDirectionRadioBox.Bind(
                wx.EVT_RADIOBOX,
                self._onShadowDirectionSelected)

        emptyFreqThresholdSlider = self._createLabeledSlider(
                'Empty threshold',
                self._checkersModel.emptyFreqThreshold * 100,
                self._onEmptyFreqThresholdSelected)

        playerDistThresholdSlider = self._createLabeledSlider(
                'Player threshold',
                self._checkersModel.playerDistThreshold * 100,
                self._onPlayerDistThresholdSelected)

        shadowDistThresholdSlider = self._createLabeledSlider(
                'Shadow threshold',
                self._checkersModel.shadowDistThreshold * 100,
                self._onShadowDistThresholdSelected)

        controlsStyle = wx.ALIGN_CENTER_VERTICAL | wx.RIGHT
        controlsBorder = 8

        controlsSizer = wx.BoxSizer(wx.HORIZONTAL)
        controlsSizer.Add(rotateBoardButton, 0,
                          controlsStyle, controlsBorder)
        controlsSizer.Add(flipBoardXButton, 0,
                          controlsStyle, controlsBorder)
        controlsSizer.Add(flipBoardYButton, 0,
                          controlsStyle, controlsBorder)
        controlsSizer.Add(shadowDirectionRadioBox, 0,
                          controlsStyle, controlsBorder)
        controlsSizer.Add(emptyFreqThresholdSlider, 0,
                          controlsStyle, controlsBorder)
        controlsSizer.Add(playerDistThresholdSlider, 0,
                          controlsStyle, controlsBorder)
        controlsSizer.Add(shadowDistThresholdSlider, 0,
                          controlsStyle, controlsBorder)

        rootSizer = wx.BoxSizer(wx.VERTICAL)
        rootSizer.Add(videosSizer)
        rootSizer.Add(controlsSizer, 0, wx.EXPAND | wx.ALL,
                      border=controlsBorder)
        self.SetSizerAndFit(rootSizer)
        
        self._captureThread = threading.Thread(
            target=self._runCaptureLoop)
        self._running = True
        self._captureThread.start()


    def _createLabeledSlider(self, label, initialValue,
                             callback):

        slider = wx.Slider(self)
        slider.SetValue(initialValue)
        slider.Bind(wx.EVT_SLIDER, callback)

        staticText = wx.StaticText(self, label=label)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(slider, 0, wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(staticText, 0, wx.ALIGN_CENTER_HORIZONTAL)
        return sizer


    def _onCloseWindow(self, event):
        self._running = False
        self._captureThread.join()
        self.Destroy()


    def _onQuitCommand(self, event):
        self.Close()


    def _onRotateBoardClicked(self, event):
        self._checkersModel.boardRotation += 1


    def _onFlipBoardXClicked(self, event):
        self._checkersModel.flipBoardX = \
            not self._checkersModel.flipBoardX


    def _onFlipBoardYClicked(self, event):
        self._checkersModel.flipBoardY = \
            not self._checkersModel.flipBoardY


    def _onShadowDirectionSelected(self, event):
        self._checkersModel.shadowDirection = event.Selection


    def _onEmptyFreqThresholdSelected(self, event):
        self._checkersModel.emptyFreqThreshold = \
                event.Selection * 0.01


    def _onPlayerDistThresholdSelected(self, event):
        self._checkersModel.playerDistThreshold = \
                event.Selection * 0.01


    def _onShadowDistThresholdSelected(self, event):
        self._checkersModel.shadowDistThreshold = \
                event.Selection * 0.01


    def _runCaptureLoop(self):
        while self._running:
            if self._checkersModel.update():
                wx.CallAfter(self._showImages)


    def _showImages(self):
        self._showImage(
            self._checkersModel.scene, self._sceneStaticBitmap,
            self._checkersModel.sceneSize)
        self._showImage(
            self._checkersModel.board, self._boardStaticBitmap,
            self._checkersModel.boardSize)


    def _showImage(self, image, staticBitmap, size):
        if image is None:
            # Provide a black bitmap.
            bitmap = wx.EmptyBitmap(size[0], size[1])
        else:
            # Convert the image to bitmap format.
            bitmap = WxUtils.wxBitmapFromCvImage(image)
        # Show the bitmap.
        staticBitmap.SetBitmap(bitmap)


def main():

    import sys
    if len(sys.argv) < 2:
        cameraDeviceID = 0
    else:
        cameraDeviceID = int(sys.argv[1])

    checkersModel = CheckersModel.CheckersModel(
            cameraDeviceID=cameraDeviceID)

    app = wx.App()
    checkers = Checkers(checkersModel)
    checkers.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
