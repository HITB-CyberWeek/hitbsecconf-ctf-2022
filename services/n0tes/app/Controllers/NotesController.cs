using System;
using System.Threading.Tasks;
using App.Models;
using App.Repositories;
using Microsoft.AspNetCore.Mvc;

namespace App.Controllers
{
    public class NotesController : Controller
    {
        private readonly INoteRepository _repository;

        public NotesController(INoteRepository repository)
        {
            _repository = repository;
        }

        [HttpGet]
        [Route("")]
        public IActionResult Index()
        {
            return View();
        }

        [HttpGet]
        [Route("/notes/")]
        [Route("/notes/{noteIdStr}")]
        public async Task<IActionResult> EditNote(string noteIdStr)
        {
            if (noteIdStr == null)
            {
                return View();
            }

            if (!Guid.TryParse(noteIdStr, out var noteId))
            {
                return BadRequest();
            }

            var note = await _repository.GetAsync(noteId, User.Identity!.Name);
            if (note == null)
            {
                return NotFound();
            }

            return View(NoteViewModel.From(note));
        }

        [HttpPost]
        [Route("/notes/")]
        [Route("/notes/{noteIdStr}")]
        public async Task<IActionResult> EditNote(string noteIdStr, NoteViewModel model)
        {
            if (!ModelState.IsValid)
            {
                return View(model);
            }

            Guid noteId;
            if (noteIdStr != null)
            {
                if (!Guid.TryParse(noteIdStr, out noteId))
                {
                    return BadRequest();
                }
            }
            else
            {
                noteId = Guid.NewGuid();
            }

            var note = model.ToNote(noteId);
            if (!await _repository.SaveAsync(note, User.Identity!.Name))
            {
                return BadRequest();
            }

            return RedirectToAction("Index");
        }
    }
}