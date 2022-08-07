using Microsoft.AspNetCore.Mvc;

namespace App.Controllers
{
    public class NotesController : Controller
    {
        public IActionResult Index()
        {
            return View();
        }
    }
}
