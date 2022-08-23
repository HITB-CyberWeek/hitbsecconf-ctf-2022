const checklogin = () => {
	let login = Cookies.get('auth')?.split(' ')[0];
	document.getElementById('auth').textContent = login || '';
	if(login) document.querySelector('.auth-buttons').style.display = 'none';
	else history.pushState(null, null, '/');
}

checklogin();

let fileId = window.location.hash?.replace(/^#/, '') || '';

const handleErrors = (response) => {
	if(!response.ok)
		throw Error(`${response.status} ${response.statusText}`);
	return response;
}

const createForm = (id, fields) => {
	const wrapper = document.createElement('form');
	fields.forEach(field => {
		const required = field === 'login' || field === 'password';
		const el = document.createElement("input");
		el.type = field === 'password' ? 'password' : 'input';
		el.name = field;
		el.placeholder = field + (required ? ' *' : '');
		el.className = 'swal-content__input' + (required ? ' required' : '');
		wrapper.appendChild(el);
	});
	return wrapper;
}

const regForm = createForm('reg', ['birthDate', 'gender', 'country', 'company', 'address', 'name', 'surname', 'patronymic', 'login', 'password', 'hobby']);
const logForm = createForm('log', ['login', 'password']);
const request = function(title, subtitle, form, path, success) {
	const args = arguments;
	swal(title, subtitle, {content: form, closeOnClickOutside: false})
		.then((value) => {
			if(!value) return;
			const data = Object.fromEntries(Array.from(new FormData(form).entries()).filter(([_, value]) => !!value?.length));
			fetch(path, { method: 'POST', headers: {'content-type': 'application/json'}, body: JSON.stringify(data) })
				.then(handleErrors).then(response => { swal('Success', success, 'success'); checklogin(); updateList(); })
				.catch(e => swal('Fail', e?.toString() ?? 'Unknown error', 'error').then(() => setTimeout(() => request.apply(this, args), 1)));
		});
}

document.getElementById('register').onclick = () => request('Register', 'About yourself', regForm, '/register', 'Registration complete');
document.getElementById('login').onclick = () => request('Login', 'Your credentials', logForm, '/login', 'Logged in');

const debounce = (ctx, func, delay) => {
	let timeout;
	return (...arguments) => {
		if(timeout) clearTimeout(timeout);
		timeout = setTimeout(() => func.apply(ctx, arguments), delay);
	}
}

const load = (id) => {
	if(!id) return;
	return fetch(`/file/${encodeURIComponent(id)}`)
		.then(handleErrors)
		.then(response => response.text())
		.then(html => {
			tinymce.activeEditor.setContent(html)
			notify('opened ' + id, 'success');
		})
		.catch(e => notify('failed to open: ' + (e?.toString() ?? 'unknown error'), 'error'));
}

tinymce.init({
	selector: 'textarea',
	entity_encoding: 'numeric',
	element_format: 'xhtml',
	width: '100%',
	height: '100%',
	plugins: [
		'advlist', 'autolink', 'link', 'lists', 'charmap', 'preview', 'anchor',
		'searchreplace', 'wordcount', 'visualblocks', 'code', 'fullscreen', 'insertdatetime',
		'table', 'emoticons', 'save', 'help'
	],
	toolbar: 'save exportbutton | undo redo | styles | bold italic | alignleft aligncenter alignright alignjustify | ' +
		'bullist numlist outdent indent | link | print preview fullscreen | ' +
		'forecolor backcolor emoticons | help',
	menu: {
		file: { title : 'File' , items : 'newdocument savedocument | preview | exportdocument' }
	},
	init_instance_callback: editor => {
		editor.on('ExecCommand', e => {
			if(e.command !== 'mceNewDocument')
				return;
			fileId = crypto.randomUUID();
			history.pushState(null, null, '/');
		});
	},
	setup: editor => {
		editor.ui.registry.addMenuItem('savedocument', {
			text: 'Save', icon: 'save',
			onAction: () => editor.execCommand('mceSave')
		});
		editor.ui.registry.addMenuItem('exportdocument', {
			text: 'Export', icon: 'export',
			onAction: () => {
				fetch(`/file/${encodeURIComponent(fileId)}?export=true`)
					.then(handleErrors)
					.then(response => response.blob().then(blob => {
						const a = document.createElement('a');
						a.href = window.URL.createObjectURL(blob);
						a.download = response.headers.get('content-disposition')?.match(/filename=['"]?([\w-]*.docx)['"]?/)?.slice(-1)[0] ?? crypto.randomUUID() + ".docx";
						document.body.appendChild(a);
						a.click();
						a.remove();
						notify('exported', 'success');
					}))
					.catch(e => notify('failed to export: ' + (e?.toString() ?? 'unknown error'), 'error'));
			}
		});
		editor.ui.registry.addButton('exportbutton', {
			icon: 'export',
			onAction: () => tinymce.activeEditor.ui.registry.getAll().menuItems['exportdocument'].onAction()
		});
		editor.on('change', () => {
			if(editor.isDirty()) editor.execCommand('mceSave');
		});
	},
	menubar: 'file edit view insert format tools table help',
	content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:16px }',
	save_onsavecallback: debounce(this, () => {
		if(!fileId) fileId = crypto.randomUUID();
		fetch(`/file/${encodeURIComponent(fileId)}`, {method: 'PUT', body: tinymce.activeEditor.getContent()})
			.then(handleErrors)
			.then(response => {
				notify('saved', 'success');
				history.pushState(null, null, '#' + encodeURIComponent(fileId));
				if(!Array.from(document.querySelectorAll('.filelink')).filter(item => item.href.endsWith(fileId)).length)
					updateList();
			})
			.catch(e => notify('failed to save: ' + (e?.toString() ?? 'unknown error'), 'error'));
	}, 300)
}).then(() => load(fileId));

const notify = (text, type) => {
	const notifier = tinymce.activeEditor.notificationManager;
	notifier.getNotifications().forEach(n => n.close());
	notifier.open({text: text, type: type, closeButton: false, timeout: 1500});
}

const updateList = () => {
	fetch('/files')
		.then(handleErrors)
		.then(response => response.json())
		.then(json => {
			if(!json) return;
			const panel = document.querySelector('.panel');
			while(panel.lastElementChild) {panel.removeChild(panel.lastElementChild);}
			const template = document.querySelector('template').content;
			const link = template.querySelector('a');
			for(let i = 0; i < json.length; i++) {
				const item = json[i];
				if(!item) continue;
				link.textContent = item.split('-')[0];
				link.href = '#' + encodeURIComponent(item);
				const clone = document.importNode(template, true);
				panel.appendChild(clone);
			}
			document.querySelectorAll("a.filelink").forEach(item => item.onclick = e => {
				e.preventDefault();
				fileId = e.target.href?.replace(/^[^#]*#/, '') || '';
				load(fileId).then(() => history.pushState(null, null, '#' + encodeURIComponent(fileId)));
			});
		})
		.catch(e => notify('failed to list files: ' + (e?.toString() ?? 'unknown error'), 'error'));
}

updateList();
