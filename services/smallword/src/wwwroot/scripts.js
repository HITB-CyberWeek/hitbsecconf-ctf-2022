let fileId = window.location.hash?.replace(/^#/, '') || '';

const checklogin = () => {
	let login = Cookies.get('auth')?.split(' ')[0];
	document.getElementById('auth').textContent = login || '';
	if(login) document.querySelector('.auth-buttons').style.display = 'none';
}

checklogin();

const handleErrors = (response) => {
	if(!response.ok)
		throw Error(`${response.status} ${response.statusText}`);
	return response;
}

const createForm = (id, fields) => {
	const wrapper = document.createElement('form');
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

const regForm = createForm('reg', ['birthDate', 'gender', 'country', 'company', 'address', 'name', 'surname', 'patronymic', 'login', 'password', 'hobby']);
const logForm = createForm('log', ['login', 'password']);
const request = (title, subtitle, form, path, success) => {
	swal(title, subtitle, {content: form})
		.then((value) => {
			if(!value) return;
			const data = Object.fromEntries(Array.from(new FormData(form).entries()).filter(([_, value]) => !!value?.length));
			fetch(path, { method: 'POST', headers: {'content-type': 'application/json'}, body: JSON.stringify(data) })
				.then(handleErrors).then(response => { swal('Success', success, 'success'); checklogin(); })
				.catch(e => swal('Fail', e?.toString() ?? 'Unknown error', 'error').then(() => setTimeout(register, 1)));
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
	const editor = tinymce.activeEditor;
	const notifier = editor.notificationManager;
	const closeall = () => notifier.getNotifications().forEach(n => n.close());
	return fetch(`/file/${encodeURIComponent(id)}`)
		.then(handleErrors)
		.then(response => response.text())
		.then(html => {
			closeall();
			editor.setContent(html)
		})
		.catch(e => {
			closeall();
			notifier.open({text: 'failed to open: ' + (e?.toString() ?? 'unknown error'), type: 'error', closeButton: false, timeout: 1500})
		});
}

tinymce.init({
	selector: 'textarea',
	entity_encoding: 'numeric',
	element_format: 'xhtml',
	width: '100%',
	height: '100%',
	plugins: [
		'advlist', 'autolink', 'link', 'lists', 'charmap', 'preview', 'anchor', 'pagebreak',
		'searchreplace', 'wordcount', 'visualblocks', 'code', 'fullscreen', 'insertdatetime',
		'table', 'emoticons', 'save', 'help'
	],
	toolbar: 'save | undo redo | styles | bold italic | alignleft aligncenter alignright alignjustify | ' +
		'bullist numlist outdent indent | link | print preview fullscreen | ' +
		'forecolor backcolor emoticons | help',
	menu: {
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
					const a = document.createElement('a');
					a.href = window.URL.createObjectURL(blob);
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
		if(!fileId) fileId = crypto.randomUUID();
		const editor = tinymce.activeEditor;
		const notifier = editor.notificationManager;
		const closeall = () => notifier.getNotifications().forEach(n => n.close());
		fetch(`/file/${encodeURIComponent(fileId)}`, {method: 'PUT', body: editor.getContent()})
			.then(handleErrors)
			.then(response => {
				closeall();
				notifier.open({text: 'saved', type: 'success', closeButton: false, timeout: 221500});
				history.pushState(null, null, '#' + encodeURIComponent(fileId));
			})
			.catch(e => {
				closeall();
				notifier.open({text: 'failed to save: ' + (e?.toString() ?? 'unknown error'), type: 'error', closeButton: false, timeout: 1500});
			});
	}, 300)
}).then(() => load(fileId));

const updateList = () => {
	fetch('/files')
		.then(handleErrors)
		.then(response => response.json())
		.then(json => {
			if(!json) return;
			const template = document.querySelector('template').content;
			const link = template.querySelector('a');
			for(let i = 0; i < json.length; i++) {
				const item = json[i];
				if(!item) continue;
				link.textContent = item.split('-')[0];
				link.href = '#' + encodeURIComponent(item);
				const clone = document.importNode(template, true);
				document.querySelector('.panel').appendChild(clone);
			}
			document.querySelectorAll("a.filelink").forEach(item => item.onclick = e => {
				e.preventDefault();
				fileId = e.target.href?.replace(/^[^#]*#/, '') || '';
				load(fileId).then(() => history.pushState(null, null, '#' + encodeURIComponent(fileId)));
			});
		})
		.catch(e => console.log(e));
}

updateList();
