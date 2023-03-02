---
title: "ClipTray (C#)"
tags: [Coding, C#]
---

Pour joindre l'utile au pédagogique, j'ai écrit mon premier _vrai_ programme en CSharp à l'aide de l'IDE [#develop](http://www.icsharpcode.net/OpenSource/SD/).  

J'avais besoin d'un programme me permettant de mettre rapidement des valeurs textes dans le presse-papier (clipboard) pour pouvoir les recopier sur une interface qui ne permettait malheureusement la pré-saisie des champs ni leur mémorisation.  

Au niveau de l'interface homme-machine, j'ai retenu le choix d'une liste accessible depuis le systray (zone de notification). Ça s'est avéré beaucoup plus simple que je pensais avec _#develop_ étant donné qu'il proposait un template pour les applications icônifiées et qu'il suffisait de remplir le reste.  

De même la fonction pour insérer des données dans le clipboard était simple à utiliser.  

Derniers trucs à régler, je voulais que le gestionnaire de l'événement pour les différents choix de la liste (copiant chacun une valeur différente dans le clipboard) soit le même : ce n'est pas très propre de réécrire la même fonction pour chaque entrée de la liste.  

Ça m'a pris plus de temps que je pensais de trouver comment faire, finalement j'ai utilisé un cast sur l'objet envoyant l'événement pour déterminer son identité et retourner dans le clipboard la valeur correspondante.  

Pour ceux que ça intéresse, [le code est sur pastebin.com](http://pastebin.com/fb5f66f) et je l'ai aussi recopié ci-dessous.  

_#develop_ génère lui-même un fichier de ressource pour spécifier l'icône à placer dans le systray. Mais avec le compilateur csc.exe de Microsoft une option `/win32icon` permet de spécifier le fichier icône (donc ça devrait marcher).

```csharp
using System;
using System.Diagnostics;
using System.Drawing;
using System.Threading;
using System.Windows.Forms;
 
namespace ClipTray
{
    public sealed class NotificationIcon
    {
        private NotifyIcon notifyIcon;
        private ContextMenu notificationMenu;
        private string[,] liste = new String[,] {
            {"TOTO", "toto"},
            {"BIDULE", "machin"}};
        
        #region Initialize icon and menu
        public NotificationIcon()
        {
            notifyIcon = new NotifyIcon();
            notificationMenu = new ContextMenu(InitializeMenu());
            
            notifyIcon.DoubleClick += IconDoubleClick;
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(NotificationIcon));
            notifyIcon.Icon = (Icon)resources.GetObject("$this.Icon");
            notifyIcon.ContextMenu = notificationMenu;
        }
        
        private MenuItem[] InitializeMenu()
        {
            MenuItem[] menu = new MenuItem[liste.GetLength(0) + 2];
            int x = 0;
            for (x = 0; x < liste.GetLength(0); x++)
            {
                menu[x] = new MenuItem(liste[x, 0], miseEnTampon);
            }
            menu[x++] = new MenuItem("About", menuAboutClick);
            menu[x++] = new MenuItem("Exit", menuExitClick);
            return menu;
        }
        #endregion
        
        #region Main - Program entry point
        /// <summary>Program entry point.</summary>
        /// <param name="args">Command Line Arguments</param>
        [STAThread]
        public static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            
            bool isFirstInstance;
            // Please use a unique name for the mutex to prevent conflicts with other programs
            using (Mutex mtx = new Mutex(true, "ClipTray", out isFirstInstance)) {
                if (isFirstInstance) {
                    NotificationIcon notificationIcon = new NotificationIcon();
                    notificationIcon.notifyIcon.Visible = true;
                    Application.Run();
                    notificationIcon.notifyIcon.Dispose();
                } else {
                    // The application is already running
                    // TODO: Display message box or change focus to existing application instance
                }
            } // releases the Mutex
        }
        #endregion
        
        #region Event Handlers
        private void menuAboutClick(object sender, EventArgs e)
        {
            MessageBox.Show("ClipTray - devloop");
        }
        
        private void menuExitClick(object sender, EventArgs e)
        {
            Application.Exit();
        }
        
        private void IconDoubleClick(object sender, EventArgs e)
        {
            MessageBox.Show("Passer par le click droit pour le menu.");
        }
        
        private void miseEnTampon(object sender, EventArgs e)
        {
            MenuItem mi = sender as MenuItem;
            int x = 0;
            for (x = 0; x < liste.GetLength(0); x++)
            {
                if (mi.Text == liste[x, 0])
                {
                    Clipboard.SetText(liste[x, 1]);
                    break;
                }
            }
        }
        #endregion
    }
}
```

*Published January 11 2011 at 13:13*
