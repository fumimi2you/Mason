using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.Windows.Ink;
using System.Diagnostics;
using System.IO;

namespace WpfDraw
{
    public partial class MainWindow : Window
    {
        List<Point> points = new List<Point>();
        Size imgSize;
        string imgPath = "";


        public static readonly DependencyProperty DraggedProperty =
            DependencyProperty.RegisterAttached("Dragged", typeof(bool), typeof(MainWindow),
            new PropertyMetadata(false));

        public static void SetDragged(DependencyObject target, bool value)
        {
            target.SetValue(DraggedProperty, value);
        }
        public static bool GetDragged(DependencyObject target)
        {
            return (bool) target.GetValue(DraggedProperty);
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
        }

        private void event_DragEnter(object sender, DragEventArgs e)
        {
            e.Effects = DragDropEffects.Copy; // ドラッグ中のカーソルを変える。
        }

        private void event_Drop(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop)) // ドロップされたものがファイルかどうか確認する。
            {
                var imgPathOrg = ((string[])e.Data.GetData(DataFormats.FileDrop))[0]; // ドロップされた最初のファイルのファイル名を得る。

                BitmapImage bmpImgPrc = new BitmapImage(); // デコードされたビットマップイメージのインスタンスを作る。
                try
                {
                    // 一度解像度を整えて、固定パスに出力
                    System.Drawing.Bitmap bmp = null;
                    {
                        BitmapImage bmpImgSrc = new BitmapImage();
                        bmpImgSrc.BeginInit();
                        bmpImgSrc.UriSource = new Uri(imgPathOrg); // ビットマップイメージのソースにファイルを指定する。
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
                    imgPath = System.IO.Path.GetDirectoryName(imgPathOrg) + "\\_tmp.jpg";
                    bmp.Save(imgPath, System.Drawing.Imaging.ImageFormat.Jpeg);
                    bmp.Dispose();

                    //  再読込
                    bmpImgPrc.BeginInit();
                    bmpImgPrc.UriSource = new Uri(imgPath); // ビットマップイメージのソースにファイルを指定する。
                    bmpImgPrc.EndInit();


                    ImageBrush imageBrush = new ImageBrush();
                    imageBrush.ImageSource = bmpImgPrc;
                    imageBrush.Stretch = Stretch.None;
                    imageBrush.AlignmentX = AlignmentX.Left;
                    imageBrush.AlignmentY = AlignmentY.Top;

                    imgSize.Width = bmpImgPrc.PixelWidth;
                    imgSize.Height = bmpImgPrc.PixelHeight;

                    canvas.Background = imageBrush; // Imageコントロールにバインディングする。

                    this.Title = System.IO.Path.GetFileName(imgPath);
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
        }

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            Ellipse elipse = new Ellipse();
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

        #region 線
        private void canvas_MouseDown(object sender, MouseButtonEventArgs e)
        {
            SetDragged(canvas, true);
            SetStartPoint(canvas, e.GetPosition(canvas));
            Debug.WriteLine(e);

            points.Clear();
            points.Add(e.GetPosition(canvas));
        }

        private void canvas_MouseMove(object sender, MouseEventArgs e)
        {
            Debug.WriteLine(e);
            if (!GetDragged(canvas))
            {
                return;
            }

            Point prev = GetStartPoint(canvas);
            Point current = e.GetPosition(canvas);

            Line lineB = new Line();
            lineB.Stroke = Brushes.Black;
            lineB.X1 = prev.X;
            lineB.Y1 = prev.Y;
            lineB.X2 = current.X;
            lineB.Y2 = current.Y;
            lineB.StrokeThickness = 2;
            canvas.Children.Add(lineB);

            Line lineW = new Line();
            lineW.Stroke = Brushes.White;
            lineW.X1 = prev.X;
            lineW.Y1 = prev.Y;
            lineW.X2 = current.X;
            lineW.Y2 = current.Y;
            lineW.StrokeThickness = 1;
            canvas.Children.Add(lineW);

            SetStartPoint(canvas, current);

            points.Add(e.GetPosition(canvas));
        }

        private void canvas_MouseUp(object sender, MouseButtonEventArgs e)
        {
            SetDragged(canvas, false);
            Debug.WriteLine(e);

            points.Add(e.GetPosition(canvas));

            string json = makeJsonStr();

            var jsonPath = System.IO.Path.Combine( System.IO.Path.GetDirectoryName(imgPath), System.IO.Path.GetFileNameWithoutExtension(imgPath) + ".json" );
            File.WriteAllText(jsonPath, json);



            //プロセスの準備
            System.Diagnostics.Process p = new System.Diagnostics.Process();
            p.StartInfo.FileName = @"C:\Miniconda3\envs\py36\python.exe";
            p.StartInfo.Arguments = @"C:\Projects\_study\Python\python-demo\Mason.py " + jsonPath + " 2";
//            p.StartInfo.CreateNoWindow = true;
            //出力を読み取れるようにする
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.RedirectStandardOutput = true;
            p.StartInfo.RedirectStandardInput = false;

            //起動
            p.Start();

            //出力を読み取る
            string results = p.StandardOutput.ReadToEnd();

            //プロセス終了まで待機する
            p.WaitForExit();
            var exitCode = p.ExitCode;
            p.Close();

        }
        #endregion

        private string makeJsonStr()
        {
            string json = "{\n";
            json += "	\"imagePath\" : \"" + imgPath.Replace("\\", "/") + "\",\n";
            json += "	\"initialContours\":[[\n";
            for(var i = 0; i < points.Count; i++)
            {
                json += "		{ \"x\":" + points[i].X + ", \"y\":" + points[i].Y + " }";
                if( i < points.Count -1 ) {
                    json += ",\n";
                } else {
                    json += "\n";
                }
            }
            json += "	]]\n}\n";
            return json;
        }
    }
}
