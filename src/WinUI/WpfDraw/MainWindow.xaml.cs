using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.IO;
using System.Threading.Tasks;

namespace PyDraw
{
    public partial class MainWindow : Window
    {
        System.Diagnostics.Process pCreated = null;
        PyController MCtrler = new PyController();

        FileInfo SRV_PY_PATH = new FileInfo(Path.Combine(System.AppDomain.CurrentDomain.BaseDirectory, @"../../../../python/mason_srv.py"));
        FileInfo INIT_IMAGE_PATH = new FileInfo(Path.Combine(System.AppDomain.CurrentDomain.BaseDirectory + @"../../../../sample/sample.jpg"));

        List<OpenCvSharp.Point> points = null;
        List<List<OpenCvSharp.Point>> fixPointss = new List<List<OpenCvSharp.Point>>();
        public static OpenCvSharp.Point ToCvPt(Point pt) { return new OpenCvSharp.Point(pt.X, pt.Y); }

        Size imgSize;
        string imgPathOrg = "";
        string imgPathTmp = "";


        public static readonly DependencyProperty DraggedProperty =
            DependencyProperty.RegisterAttached("Dragged", typeof(bool), typeof(MainWindow),
            new PropertyMetadata(false));

        public static void SetDragged(DependencyObject target, bool value)
        {
            target.SetValue(DraggedProperty, value);
        }
        public static bool GetDragged(DependencyObject target)
        {
            return (bool)target.GetValue(DraggedProperty);
        }


        public static readonly DependencyProperty StartPointProperty =
            DependencyProperty.RegisterAttached("StartPoint",
            typeof(Point),
            typeof(MainWindow),
            new UIPropertyMetadata(new Point()));

        public static Point GetStartPoint(DependencyObject obj)
        {
            return (Point)obj.GetValue(StartPointProperty);
        }

        public static void SetStartPoint(DependencyObject obj, Point value)
        {
            obj.SetValue(StartPointProperty, value);
        }

        public MainWindow()
        {
            InitializeComponent();

            if (MCtrler.PyExistsCheck() < 0)
            {
                StartSrvPy();
                if (MCtrler.PyExistsCheck() < 0)
                {
                    MessageBox.Show("srv.py が起動しとらんでー");
                }
            }

            if (File.Exists(INIT_IMAGE_PATH.FullName))
            {
                imgPathOrg = INIT_IMAGE_PATH.FullName;
                imgPathTmp = MakeTmpImg(imgPathOrg);

                MCtrler.SetImage(imgPathOrg);
                LoadImage();
            }
        }

        ~MainWindow()
        {
            MCtrler.Close();
            if (pCreated != null)
            {
                pCreated.Close();
//                pCreated.Kill();
            }
        }

        private static string MakeTmpImg(string pathOrg)
        {
            // 一度解像度を整えて、固定パスに出力
            System.Drawing.Bitmap bmp = null;
            {
                BitmapImage bmpImgSrc = new BitmapImage();
                bmpImgSrc.BeginInit();
                bmpImgSrc.UriSource = new Uri(pathOrg); // ビットマップイメージのソースにファイルを指定する。
                bmpImgSrc.EndInit();

                var encoder = new System.Windows.Media.Imaging.BmpBitmapEncoder();
                encoder.Frames.Add(System.Windows.Media.Imaging.BitmapFrame.Create(bmpImgSrc));
                using (var ms = new System.IO.MemoryStream())
                {
                    encoder.Save(ms);
                    ms.Seek(0, System.IO.SeekOrigin.Begin);
                    using (var temp = new System.Drawing.Bitmap(ms))
                    {
                        // このおまじないの意味は参考資料を参照
                        bmp = new System.Drawing.Bitmap(temp);
                    }
                }
            }
            // 解像度設定
            bmp.SetResolution(96, 96);

            // 一度固定ファイルとして保存
            var pathTmp = System.IO.Path.GetTempPath() + System.Environment.TickCount.ToString() + ".jpg";
            bmp.Save(pathTmp, System.Drawing.Imaging.ImageFormat.Jpeg);
            bmp.Dispose();

            return pathTmp;
        }

        private void LoadImage()
        {
            BitmapImage bmpImgPrc = new BitmapImage(); // デコードされたビットマップイメージのインスタンスを作る。
            try
            {
                bmpImgPrc.BeginInit();
                bmpImgPrc.UriSource = new Uri(imgPathTmp); // ビットマップイメージのソースにファイルを指定する。
                bmpImgPrc.EndInit();


                ImageBrush imageBrush = new ImageBrush();
                imageBrush.ImageSource = bmpImgPrc;
                imageBrush.Stretch = Stretch.Fill;
                imageBrush.AlignmentX = AlignmentX.Center;
                imageBrush.AlignmentY = AlignmentY.Center;

                imgSize.Width = bmpImgPrc.PixelWidth;
                imgSize.Height = bmpImgPrc.PixelHeight;

                canvas.Background = imageBrush; // Imageコントロールにバインディングする。

                this.Title = System.IO.Path.GetFileName(imgPathOrg);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void event_DragEnter(object sender, DragEventArgs e)
        {
            e.Effects = DragDropEffects.Copy; // ドラッグ中のカーソルを変える。
        }

        private void event_Drop(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop)) // ドロップされたものがファイルかどうか確認する。
            {
                imgPathOrg = ((string[])e.Data.GetData(DataFormats.FileDrop))[0]; // ドロップされた最初のファイルのファイル名を得る。
                imgPathTmp = MakeTmpImg(imgPathOrg);
                
                MCtrler.SetImage(imgPathOrg);
                LoadImage();
            }
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            var elipse = new System.Windows.Shapes.Ellipse();
            elipse.Fill = Brushes.Aqua;
            elipse.Width = 100;
            elipse.Height = 100;
            elipse.PreviewMouseDown += new MouseButtonEventHandler(elipse_MouseDown);
            elipse.PreviewMouseMove += new MouseEventHandler(elipse_MouseMove);
            elipse.PreviewMouseUp += new MouseButtonEventHandler(elipse_MouseUp);
            canvas.Children.Add(elipse);
        }

        void elipse_MouseUp(object sender, MouseButtonEventArgs e)
        {
            UIElement obj = sender as UIElement;
            if (obj == null || !GetDragged(obj))
            {
                return;
            }
            e.Handled = true;
            SetDragged(sender as DependencyObject, false);
        }

        void elipse_MouseMove(object sender, MouseEventArgs e)
        {
            UIElement obj = sender as UIElement;
            if (obj == null || !GetDragged(obj))
            {
                return;
            }

            e.Handled = true;
            Point start = GetStartPoint(obj);
            Canvas.SetTop(obj, e.GetPosition(canvas).Y - start.Y);
            Canvas.SetLeft(obj, e.GetPosition(canvas).X - start.X);
        }

        void elipse_MouseDown(object sender, MouseButtonEventArgs e)
        {
            e.Handled = true;
            SetDragged(sender as DependencyObject, true);
            SetStartPoint(sender as DependencyObject, e.GetPosition(sender as IInputElement));
        }

        private void canvas_MouseDown(object sender, MouseButtonEventArgs e)
        {
            SetDragged(canvas, true);
            SetStartPoint(canvas, e.GetPosition(canvas));

            points = new List<OpenCvSharp.Point>();
            points.Add(ToCvPt(e.GetPosition(canvas)));
        }

        private void canvas_MouseMove(object sender, MouseEventArgs e)
        {
            if (!GetDragged(canvas)) { return; }

            Point prev = GetStartPoint(canvas);
            Point current = e.GetPosition(canvas);

            var lineB = new System.Windows.Shapes.Line();
            lineB.Stroke = Brushes.Black;
            lineB.X1 = prev.X;
            lineB.Y1 = prev.Y;
            lineB.X2 = current.X;
            lineB.Y2 = current.Y;
            lineB.StrokeThickness = 2;
            canvas.Children.Add(lineB);

            var lineW = new System.Windows.Shapes.Line();
            lineW.Stroke = Brushes.White;
            lineW.X1 = prev.X;
            lineW.Y1 = prev.Y;
            lineW.X2 = current.X;
            lineW.Y2 = current.Y;
            lineW.StrokeThickness = 1;
            canvas.Children.Add(lineW);

            SetStartPoint(canvas, current);

            points.Add(ToCvPt(e.GetPosition(canvas)));
        }


        private void canvas_MouseUp(object sender, MouseButtonEventArgs e)
        {
            SetDragged(canvas, false);

            if(points==null) {
                return;
            }

            points.Add(ToCvPt(e.GetPosition(canvas)));

            var pointsImg = new List<OpenCvSharp.Point>();
            foreach ( var pt in points) {
                pointsImg.Add(new OpenCvSharp.Point(
                    pt.X * imgSize.Width / canvas.ActualWidth,
                    pt.Y * imgSize.Height / canvas.ActualHeight));
            }

            var addPointss = new List<List<OpenCvSharp.Point>>();
            var subPointss = new List<List<OpenCvSharp.Point>>();

            //  モードを確認して輪郭追加
            var extMode = this.cmbExtType.SelectedIndex;
            if (extMode == 1) {
                subPointss.Add(OpenCvSharp.Cv2.ApproxPolyDP(pointsImg, 4, true).ToList());
            } else {
                addPointss.Add(OpenCvSharp.Cv2.ApproxPolyDP(pointsImg, 4, true).ToList());
            }

            //  pythonの実行
            var retPtss = MCtrler.ProcCore(fixPointss, addPointss, subPointss);
            int valid = 0;
            if (retPtss != null) {
                foreach (var cont in retPtss) { valid += retPtss.Count; }
            }
            if (valid == 0)
            {
                MessageBox.Show("検出に失敗しとるで");
                canvas.Children.Clear();
                LoadImage();
                return;
            }

            //  結果の描画
            canvas.Children.Clear();
            fixPointss = retPtss;
            var imgOrg = OpenCvSharp.Cv2.ImRead(imgPathOrg);
            var imgMask = new OpenCvSharp.Mat(imgOrg.Size(), OpenCvSharp.MatType.CV_8UC3, new OpenCvSharp.Scalar(0,0,0));
            imgMask.DrawContours(fixPointss.Cast<IEnumerable<OpenCvSharp.Point>>(), -1, new OpenCvSharp.Scalar(255,255,255), -1, OpenCvSharp.LineTypes.AntiAlias);
            var imgMasked = imgOrg & imgMask;
            var imgRet = new OpenCvSharp.Mat();
            OpenCvSharp.Cv2.Max(imgOrg.Clone() / 4, imgMasked, imgRet);

            if (false)
            {
                OpenCvSharp.Cv2.ImShow("imgOrg", imgOrg);
                OpenCvSharp.Cv2.ImShow("imgMasked", imgMasked);
                OpenCvSharp.Cv2.ImShow("imgMask", imgMask);
                OpenCvSharp.Cv2.ImShow("imgRet", imgRet);
                OpenCvSharp.Cv2.WaitKey(0);
            }

            imgPathTmp = System.IO.Path.GetTempPath() + System.Environment.TickCount.ToString() + ".jpg";
            OpenCvSharp.Cv2.ImWrite(imgPathTmp, imgRet);
            LoadImage();
        }

        private async void StartSrvPy()
        {
            //プロセスの準備
            pCreated = new System.Diagnostics.Process();
            pCreated.StartInfo.FileName = "python";
            pCreated.StartInfo.Arguments = SRV_PY_PATH.FullName;
            pCreated.StartInfo.CreateNoWindow = true;

            //出力を読み取れるようにする
            //pCreated.StartInfo.UseShellExecute = false;
            //pCreated.StartInfo.RedirectStandardOutput = true;
            //pCreated.StartInfo.RedirectStandardInput = false;

            //起動
            pCreated.Start();

            //出力を読み取る
            //string results = pCreated.StandardOutput.ReadToEnd();

            await Task.Delay(1000);

            //Console.Write(results);
        }
    }
}
