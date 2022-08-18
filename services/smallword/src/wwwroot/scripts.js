var fileId = window.location.hash?.replace(/^#/, '') || '';

let login = Cookies.get('auth')?.split(' ')[0];
document.getElementById('auth').textContent = login || '';

const handleErrors = (response) => {
	if(!response.ok)
		throw Error(`${response.status} ${response.statusText}`);
	return response;
}

const createForm = (id, fields) => {
	let wrapper = document.createElement('form');
	fields.forEach(field => {
		let el = document.createElement("input");
		el.type = field === 'password' ? 'password' : 'input';
		el.name = field;
		el.placeholder = field;
		el.className = 'swal-content__input';
		wrapper.appendChild(el);
	});
	return wrapper;
}

let regForm = createForm('reg', ['birthDate', 'gender', 'country', 'company', 'address', 'name', 'surname', 'patronymic', 'login', 'password']);
let logForm = createForm('log', ['login', 'password']);
const request = (title, subtitle, form, path, success) => {
	swal(title, subtitle, {content: form})
		.then((value) => {
			if(!value) return;
			const data = Object.fromEntries(new FormData(form).entries());
			fetch(path, { method: 'POST', headers: {'content-type': 'application/json'}, body: JSON.stringify(data) })
				.then(handleErrors).then(response => swal('Success', success, 'success'))
				.catch(e => swal('Fail', e?.toString() ?? 'Unknown error', 'error').then(() => setTimeout(register, 1)));
		});
}

document.getElementById('register').onclick = () => request('Register', 'About yourself', regForm, '/register', 'Registration complete');
document.getElementById('login').onclick = () => request('Login', 'Your credentials', logForm, '/login', 'Logged in');

const debounce = (ctx, func, delay) => {
	let timeout;
	return (...arguments) => {
		if(timeout) {
			clearTimeout(timeout);
		}

		timeout = setTimeout(() => {
			func.apply(ctx, arguments);
		}, delay);
	}
}

tinymce.init({
	selector: 'textarea',
	entity_encoding: 'numeric',
	element_format: 'xhtml',
	//width: 600,
	//height: 300,
	plugins: [
		'advlist', 'autolink', 'link', 'lists', 'charmap', 'preview', 'anchor', 'pagebreak',
		'searchreplace', 'wordcount', 'visualblocks', 'code', 'fullscreen', 'insertdatetime',
		'table', 'emoticons', 'save', 'help'
	],
	toolbar: 'save | undo redo | styles | bold italic | alignleft aligncenter alignright alignjustify | ' +
		'bullist numlist outdent indent | link | print preview fullscreen | ' +
		'forecolor backcolor emoticons | help',
	menu: {
		//favs: { title: 'My Favorites', items: 'code visualaid | searchreplace | emoticons' }
		file: { title : 'File' , items : 'newdocument savedocument | preview | exportdocument' }
	},
	setup: (editor) => {
		editor.ui.registry.addMenuItem('savedocument', {
			text: 'Save',
			onAction: () => editor.execCommand('mceSave')
		});
		editor.ui.registry.addMenuItem('exportdocument', {
			text: 'Export',
			onAction: () => {
				fetch(`/file/${encodeURIComponent(fileId)}?export=true`)
				.then(handleErrors)
				.then(response => response.blob())
				.then(blob => {
					var url = window.URL.createObjectURL(blob);
					var a = document.createElement('a');
					a.href = url;
					document.body.appendChild(a);
					a.click();
					a.remove();
				})
				.catch(e => swal('Failed to export', e?.toString() ?? 'Unknown error', 'error'));
			}
		});
		editor.on('change', () => {
			if(editor.isDirty()) editor.execCommand('mceSave');
		})
	},
	menubar: 'file edit view insert format tools table help',
	content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:16px }',
	save_onsavecallback: debounce(this, () => {
		let editor = tinymce.activeEditor;
		if(!fileId) fileId = crypto.randomUUID();
		const closeall = () => editor.notificationManager.getNotifications().forEach(n => n.close());
		fetch(`/file/${encodeURIComponent(fileId)}`, {method: 'PUT', body: editor.getContent()})
			.then(handleErrors)
			.then(response => {
				closeall();
				editor.notificationManager.open({text: 'saved', type: 'success', closeButton: false, timeout: 1500});
				history.pushState(null, null, '#' + encodeURIComponent(fileId));
			})
			.catch(e => {
				closeall();
				editor.notificationManager.open({text: 'failed to save: ' + (e?.toString() ?? 'unknown error'), type: 'error', closeButton: false, timeout: 1500});
			});
	}, 300)
}).then(() => {
	let editor = tinymce.activeEditor;
	if(!!fileId) {
		fetch(`/file/${encodeURIComponent(fileId)}`)
			.then(handleErrors)
			.then(response => response.text())
			.then(html => editor.setContent(html))
			.catch(e => editor.notificationManager.open({text: 'failed to open: ' + (e?.toString() ?? 'unknown error'), type: 'error', closeButton: false, timeout: 1500}));
	}
});

const updateList = () => {
	fetch('/files')
		.then(handleErrors)
		.then(response => response.json())
		.then(json => {
			if(!json) return;
			for(var i = 0; i < json.length; i++) {
				let item = json[i];
				if(!item) continue;
				let template = document.querySelector('template').content;
				let link = template.querySelector('a');
				link.textContent = item.split('-')[0];
				link.href = '/?r=' + crypto.randomUUID().slice(0,8) + '#' + encodeURIComponent(item);
				let clone = document.importNode(template, true);
				document.querySelector('table').appendChild(clone);
			}
		})
		.catch(e => console.log(e));
}

updateList();
