using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using System.Collections.Generic;
using System.Windows.Forms;

// A small native .NET launcher. The adjacent, hash-pinned ZIP contains every
// runtime/model file; PowerShell streams it straight to the installation drive.
internal static class SetupLauncher
{
    internal static Dictionary<string, object> Release;
    internal static string Folder = AppDomain.CurrentDomain.BaseDirectory;
    internal static string Value(string key) { return (string)Release[key]; }
    internal static string Payload { get { return Path.Combine(Folder, Value("payload")); } }

    [STAThread]
    private static int Main(string[] args)
    {
        try
        {
            using (var input = Assembly.GetExecutingAssembly().GetManifestResourceStream("release.json"))
            using (var reader = new StreamReader(input, Encoding.UTF8))
                Release = new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(reader.ReadToEnd());
            if (!Environment.Is64BitOperatingSystem) throw new Exception("BiliClass cần Windows 10/11 64-bit.");
            if (args.Length > 0 && args[0] == "--verify") { VerifyPayload(); return 0; }
            if (args.Length == 2 && args[0] == "--install-test")
            {
                VerifyDestination(args[1]);
                VerifyPayload();
                Install(args[1], false, false, delegate(int progress, string message) { });
                return 0;
            }
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            if (args.Length == 2 && args[0] == "--smoke")
            {
                using (var form = new SetupForm())
                {
                    form.Show(); Application.DoEvents();
                    using (var bitmap = new Bitmap(form.Width, form.Height))
                    { form.DrawToBitmap(bitmap, new Rectangle(0, 0, form.Width, form.Height)); bitmap.Save(args[1], System.Drawing.Imaging.ImageFormat.Png); }
                    form.Close();
                }
                return 0;
            }
            Application.Run(new SetupForm());
            return 0;
        }
        catch (Exception error)
        {
            File.WriteAllText(Path.Combine(Path.GetTempPath(), "BiliClass-setup-error.txt"), error.ToString(), Encoding.UTF8);
            if (args.Length == 0) MessageBox.Show(error.Message, "Chưa cài được BiliClass", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }

    internal static void VerifyPayload()
    {
        if (!File.Exists(Payload)) throw new Exception("Hãy để file BiliClass-Setup.exe và gói dữ liệu .zip trong cùng một thư mục.");
        using (var input = File.OpenRead(Payload))
        using (var sha = SHA256.Create())
        {
            string digest = BitConverter.ToString(sha.ComputeHash(input)).Replace("-", "").ToLowerInvariant();
            if (digest != Value("sha256")) throw new Exception("Gói dữ liệu chưa đầy đủ hoặc bị thay đổi. Vui lòng chép lại cả thư mục bộ cài.");
        }
    }

    private static string Literal(string value) { return "'" + value.Replace("'", "''") + "'"; }

    internal static string VerifyDestination(string directory)
    {
        if (String.IsNullOrWhiteSpace(directory)) throw new Exception("Hãy chọn thư mục cài BiliClass.");
        string root = Path.GetFullPath(directory).TrimEnd(Path.DirectorySeparatorChar);
        if (root == Path.GetPathRoot(root).TrimEnd(Path.DirectorySeparatorChar))
            throw new Exception("Hãy tạo một thư mục riêng để cài BiliClass, ví dụ D:\\BiliClass-App. Không chọn cả ổ đĩa.");
        if (File.Exists(root)) throw new Exception("Đường dẫn đã chọn là một tệp. Hãy chọn một thư mục mới để cài BiliClass.");
        if (!Directory.Exists(root)) return root;
        if (File.Exists(Path.Combine(root, "library.db")))
            throw new Exception("Đây là thư viện bài giảng. Hãy chọn một thư mục khác để cài ứng dụng, ví dụ D:\\BiliClass-App.\n\n" + root);
        string marker = Path.Combine(root, ".biliclass-install.json");
        if (!File.Exists(marker))
        {
            using (var entries = Directory.EnumerateFileSystemEntries(root).GetEnumerator())
                if (entries.MoveNext()) throw new Exception("Thư mục này đã có dữ liệu. Hãy chọn hoặc tạo một thư mục mới, trống hoàn toàn để cài BiliClass, ví dụ D:\\BiliClass-App.\n\nKhông chọn thư mục đang chứa bộ cài và không cần xóa dữ liệu hiện có.\n\nThư mục đã chọn: " + root);
        }
        else
        {
            bool verified = false;
            try
            {
                var info = new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(File.ReadAllText(marker, Encoding.UTF8));
                object product, previousRoot;
                verified = info != null && info.TryGetValue("product", out product) && Object.Equals(product, "BiliClass")
                    && info.TryGetValue("root", out previousRoot) && previousRoot is string
                    && String.Equals((string)previousRoot, root, StringComparison.OrdinalIgnoreCase);
            }
            catch { }
            if (!verified) throw new Exception("Chưa xác nhận được bản BiliClass trong thư mục này. Hãy chọn một thư mục mới để cài; dữ liệu hiện có được giữ nguyên.\n\n" + root);
        }
        // PowerShell verifies every existing version file against the payload
        // before repairing shortcuts; a failed shortcut step can be retried.
        return root;
    }

    internal static void Install(string directory, bool shortcuts, bool launch, Action<int, string> progress)
    {
        string root = VerifyDestination(directory);
        string work = Path.Combine(Path.GetTempPath(), "BiliClassSetup-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(work);
        try
        {
            string script = Path.Combine(work, "Install-BiliClass.ps1");
            using (var input = Assembly.GetExecutingAssembly().GetManifestResourceStream("Install-BiliClass.ps1"))
            using (var output = File.Create(script)) input.CopyTo(output);
            string command = "$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue';"
                + "[Console]::OutputEncoding=New-Object Text.UTF8Encoding($false);$OutputEncoding=[Console]::OutputEncoding;try { & " + Literal(script)
                + " -InstallRoot " + Literal(root) + " -PackageZip " + Literal(Payload)
                + " -ExpectedVersion " + Literal(Value("version"))
                + (shortcuts ? "" : " -NoShortcuts") + (launch ? " -LaunchAfterInstall" : "")
                + "; exit 0 } catch { [Console]::Out.WriteLine('BILICLASS_ERROR|' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($_.Exception.Message)));exit 1 }";
            string powershell = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.System), "WindowsPowerShell", "v1.0", "powershell.exe");
            var start = new ProcessStartInfo(powershell, "-NoProfile -NonInteractive -InputFormat Text -OutputFormat Text -ExecutionPolicy Bypass -EncodedCommand "
                + Convert.ToBase64String(Encoding.Unicode.GetBytes(command)));
            start.UseShellExecute = false; start.CreateNoWindow = true;
            start.RedirectStandardOutput = true; start.RedirectStandardError = true;
            start.StandardOutputEncoding = Encoding.UTF8; start.StandardErrorEncoding = Encoding.UTF8;
            var log = new StringBuilder();
            var errors = new StringBuilder();
            string failure = null;
            using (var process = new Process())
            {
                process.StartInfo = start;
                process.OutputDataReceived += delegate(object sender, DataReceivedEventArgs line)
                {
                    if (line.Data == null) return;
                    lock (log) log.AppendLine(line.Data);
                    if (line.Data.StartsWith("BILICLASS_ERROR|", StringComparison.Ordinal))
                    {
                        try { failure = Encoding.UTF8.GetString(Convert.FromBase64String(line.Data.Substring("BILICLASS_ERROR|".Length))); }
                        catch (FormatException) { }
                    }
                    if (line.Data.StartsWith("PROGRESS|"))
                    {
                        string[] parts = line.Data.Split('|'); int percent;
                        if (parts.Length >= 3 && int.TryParse(parts[1], out percent)) progress(percent, "Đang cài đặt… " + percent + "%");
                    }
                };
                process.ErrorDataReceived += delegate(object sender, DataReceivedEventArgs line)
                { if (line.Data != null) lock (errors) errors.AppendLine(line.Data); };
                process.Start(); process.BeginOutputReadLine(); process.BeginErrorReadLine();
                process.WaitForExit();
                string logFolder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "BiliClass", "logs");
                Directory.CreateDirectory(logFolder);
                string logFile = Path.Combine(logFolder, "setup-" + DateTime.UtcNow.ToString("yyyyMMdd-HHmmss") + ".log");
                File.WriteAllText(logFile, log.ToString() + errors.ToString(), Encoding.UTF8);
                if (process.ExitCode != 0) throw new Exception((String.IsNullOrWhiteSpace(failure)
                    ? "Chưa hoàn tất cài đặt. Hãy thử lại hoặc gửi tệp nhật ký bên dưới để kiểm tra." : failure.Trim())
                    + "\n\nChi tiết: " + logFile);
            }
        }
        finally
        {
            // Only this launcher's unique temporary directory is removed.
            if (Directory.Exists(work)) Directory.Delete(work, true);
        }
    }
}

internal sealed class SetupForm : Form
{
    private TextBox destination;
    private Button install, browse;
    private CheckBox shortcuts, launch;
    private Label status;
    private ProgressBar progress;
    private bool busy;

    internal SetupForm()
    {
        Text = "Cài đặt BiliClass " + SetupLauncher.Value("version") + " · Bộ cài 2";
        Font = new Font("Segoe UI", 10);
        AutoScaleMode = AutoScaleMode.Dpi; ClientSize = new Size(650, 415);
        FormBorderStyle = FormBorderStyle.FixedDialog; MaximizeBox = false;
        StartPosition = FormStartPosition.CenterScreen;
        Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath);
        var title = new Label { Text = "BiliClass", Font = new Font("Segoe UI", 26, FontStyle.Bold),
            ForeColor = Color.FromArgb(17, 38, 80), Location = new Point(26, 20), AutoSize = true };
        Controls.Add(title);
        Controls.Add(new Label { Text = "Bộ cài đầy đủ · " + SetupLauncher.Value("version")
            + "\nCó sẵn giọng Việt–Mỹ, OCR, mẫu bài giảng và mascot.", Location = new Point(28, 82), Size = new Size(595, 52) });
        Controls.Add(new Label { Text = "Thư mục cài ứng dụng:", Location = new Point(28, 147), AutoSize = true });
        string defaultPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs", "BiliClass");
        try { if (Directory.Exists("F:\\") && new DriveInfo("F:\\").DriveType == DriveType.Fixed) defaultPath = "F:\\Applications\\BiliClass"; } catch { }
        destination = new TextBox { Text = defaultPath, Location = new Point(28, 174), Size = new Size(493, 28) };
        browse = new Button { Text = "Chọn…", Location = new Point(531, 171), Size = new Size(90, 32) };
        browse.Click += delegate { using (var dialog = new FolderBrowserDialog { Description = "Chọn thư mục cài BiliClass, tách riêng thư viện bài giảng", SelectedPath = destination.Text })
            if (dialog.ShowDialog(this) == DialogResult.OK) destination.Text = dialog.SelectedPath; };
        Controls.Add(destination); Controls.Add(browse);
        shortcuts = new CheckBox { Text = "Tạo biểu tượng trên Desktop và Start menu", Checked = true, Location = new Point(28, 218), AutoSize = true };
        launch = new CheckBox { Text = "Mở BiliClass sau khi cài xong", Checked = true, Location = new Point(28, 246), AutoSize = true };
        Controls.Add(shortcuts); Controls.Add(launch);
        status = new Label { Text = "Chọn thư mục mới/trống để cài, khác thư mục đang chứa bộ cài.\nBài giảng và thư viện cá nhân được giữ riêng với ứng dụng.", Location = new Point(28, 291), Size = new Size(593, 36) };
        progress = new ProgressBar { Location = new Point(28, 333), Size = new Size(593, 14) };
        install = new Button { Text = "Cài đặt", Location = new Point(501, 365), Size = new Size(120, 34) };
        install.Click += BeginInstall;
        Controls.Add(status); Controls.Add(progress); Controls.Add(install);
        FormClosing += delegate(object sender, FormClosingEventArgs e) { if (busy) e.Cancel = true; };
    }

    private async void BeginInstall(object sender, EventArgs e)
    {
        string root = destination.Text.Trim(); bool createShortcuts = shortcuts.Checked, open = launch.Checked;
        busy = true; install.Enabled = destination.Enabled = browse.Enabled = shortcuts.Enabled = launch.Enabled = false;
        status.Text = "Đang kiểm tra gói dữ liệu đầy đủ…"; progress.Style = ProgressBarStyle.Marquee;
        try
        {
            SetupLauncher.VerifyDestination(root);
            await Task.Run(delegate
            {
                SetupLauncher.VerifyPayload();
                SetupLauncher.Install(root, createShortcuts, open, delegate(int percent, string message)
                { BeginInvoke((Action)delegate { progress.Style = ProgressBarStyle.Continuous; progress.Value = Math.Min(100, percent); status.Text = message; }); });
            });
            status.Text = "Đã cài đặt xong. Mở BiliClass từ Desktop hoặc Start menu.";
            progress.Style = ProgressBarStyle.Continuous; progress.Value = 100;
            install.Text = "Hoàn tất"; install.Click -= BeginInstall; install.Click += delegate { Close(); };
        }
        catch (Exception error)
        {
            progress.Style = ProgressBarStyle.Continuous; progress.Value = 0;
            status.Text = "Chưa cài được. Bạn có thể chọn lại thư mục và thử lại.";
            MessageBox.Show(this, error.Message, "BiliClass", MessageBoxButtons.OK, MessageBoxIcon.Error);
            destination.Enabled = browse.Enabled = shortcuts.Enabled = launch.Enabled = true;
        }
        finally { busy = false; install.Enabled = true; }
    }
}
