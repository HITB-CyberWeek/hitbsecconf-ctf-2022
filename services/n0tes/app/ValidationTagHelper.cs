using System.Text.Encodings.Web;
using Microsoft.AspNetCore.Mvc.TagHelpers;
using Microsoft.AspNetCore.Razor.TagHelpers;

namespace App
{
    [HtmlTargetElement("input", Attributes = "has-errors")]
    public class ValidationTagHelper : TagHelper
    {
        public bool HasErrors { get; set; }

        public override void Process(TagHelperContext context, TagHelperOutput output)
        {
            base.Process(context, output);

            if (HasErrors)
            {
                output.AddClass("is-invalid", HtmlEncoder.Default);
            }
        }
    }
}