from ._anvil_designer import GuidesTemplate
from anvil import *
import anvil.js
import json

from .. import ui, state, i18n
from ..i18n import t
from ..icons import icon
from ..content import GUIDES, GUIDE_SLUGS, GUIDE_SITUATIONS, guide_cover

STORE_KEY = 'aa.guides'  # this browser already unlocked the guides: {slug: url}


def _saved():
  try:
    raw = anvil.js.window.localStorage.getItem(STORE_KEY)
    links = json.loads(raw) if raw else {}
    return {k: v for k, v in links.items() if k in GUIDE_SLUGS and isinstance(v, str)} or None
  except Exception:
    return None


def _save(links):
  try:
    anvil.js.window.localStorage.setItem(STORE_KEY, json.dumps(links))
  except Exception:
    pass


def _download(slug, url, title, cls='accent sm'):
  name = ui.esc('Addanapp - ' + title + '.pdf')
  return (f'<a class="aa-btn {cls}" href="{ui.esc(url)}" download="{name}" target="_blank" rel="noopener" data-dl="{slug}">'
          f'{icon("file", "width=16 height=16")} {t("Download PDF")}</a>')


class Guides(GuidesTemplate):
  """#guides[/slug]: the free guides. One email unlocks all five: the download links appear on the page
  and are emailed too (api_public.request_guides). The PDFs are theme assets, so this is a soft gate."""

  def __init__(self, focus=None, **properties):
    self.init_components(**properties)
    self.focus = focus if focus in GUIDE_SLUGS else ''
    self.links = _saved()
    final_title = t("Read one and thought it was about you? <em>Let's scope it.</em>")
    lang_note = (f'<p class="gd-lang">{icon("lang", "width=16 height=16")} {t("The guides are written in English.")}</p>'
                 if i18n.lang != 'en' else '')
    self.html = f'''
    <div class="lp">
      <section class="lp-hero gd-hero" aria-labelledby="gd-h">
        <div class="aa-wrap grid">
          <div>
            <div class="eyebrow rv">{t('Free guides')}</div>
            <h1 id="gd-h" class="rv d1">{t('Short guides for people who <em>run things.</em>')}</h1>
            <p class="sub rv d2">{t("Five practical PDFs for owners and managers: when a spreadsheet has become an app, how to get a fixed price for software, what to demand from AI-assisted developers, build or buy, and Québec's Law 25.")}</p>
            <div class="assure rv d3">
              <span>{icon('check')}{t('Free, no sales call')}</span>
              <span>{icon('check')}{t('About ten pages each')}</span>
              <span>{icon('check')}{t('Every number sourced')}</span>
            </div>
            {lang_note}
          </div>
          <div class="lp-form gd-form rv d2" id="guide-form">
            <div class="form-body">
              <h3 style="font-size:1.3rem;margin-bottom:4px">{t('Get all five guides free')}</h3>
              <p class="small muted" style="margin-bottom:20px">{t('Enter your email and the download links appear right away. We email them to you as well.')}</p>
              <div class="aa-error hidden"></div>
              <div class="row2">
                <div class="f"><label for="gd-email">{t('Work email')}</label><input id="gd-email" type="email" name="email" autocomplete="email" placeholder="{t('jane@company.com')}"></div>
                <div class="f"><label for="gd-name">{t('First name')} <span class="opt">{t('(optional)')}</span></label><input id="gd-name" type="text" name="name" autocomplete="given-name" placeholder="{t('Jane')}"></div>
              </div>
              <div class="f"><label for="gd-sit">{t("What's closest to your situation?")} <span class="opt">{t('(optional)')}</span></label>
                <select id="gd-sit" name="situation"><option value="">{t('Choose one')}</option>{''.join(f'<option value="{ui.esc(x)}">{t(x)}</option>' for x in GUIDE_SITUATIONS)}</select></div>
              <input class="hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
              <label class="check" style="margin-bottom:18px"><input type="checkbox" name="newsletter"><span>{t('Yes, also send me occasional tips from Addanapp. I can unsubscribe at any time.')}</span></label>
              <button type="button" class="aa-btn accent block lg" data-act="get">{t('Get the guides')} <span class="arr">&rarr;</span></button>
              <p class="tiny muted" style="margin:14px 0 0">{t('We use your email to send you the guides and, only if you tick the box, occasional tips. We never sell it. See our <a href="javascript:void(0)" data-lk-open="privacy">privacy policy</a>.')}</p>
            </div>
            <div class="ok hidden">
              <div class="seal">{icon('check')}</div>
              <h3 style="font-size:1.4rem">{t('Your guides are ready')}</h3>
              <p class="muted js-sent">{t("We've also emailed you the links, so you can come back to them later.")}</p>
              <div class="gd-list js-list"></div>
              <p class="tiny muted" style="margin:16px 0 0">{t('Recognise your business in one of them?')} <a href="#home/contact">{t('Send us a brief')}</a></p>
            </div>
          </div>
        </div>
      </section>
      <section class="lp-sec" style="padding-top:72px">
        <div class="aa-wrap"><div class="gd-grid js-cards"></div></div>
      </section>
      <section class="lp-sec tight lp-alt">
        <div class="aa-wrap lp-final">
          <div class="eyebrow" style="justify-content:center">{t('Your turn')}</div>
          <h2>{final_title}</h2>
          <p>{t('Send a short brief. An engineer, not a salesperson, will reply with questions or a fixed quote.')}</p>
          <div class="ctas"><a class="aa-btn accent lg" href="#home/contact">{t('Start a project')} <span class="arr">&rarr;</span></a></div>
        </div>
      </section>
    </div>'''
    self.node = ui.dom(self)
    self.form = self.node.querySelector('#guide-form')
    ui.bind(self, {'get': lambda a: self._submit(), 'want': self._want})
    self._render(just_sent=False)
    self.add_event_handler('show', self.form_show)
    ui.reveal(self)

  def form_show(self, **event_args):
    ui.reveal(self)
    if self.focus:
      card = self.node.querySelector('#g-' + self.focus)
      if card is not None:
        card.classList.add('focus')
        card.scrollIntoView({'behavior': 'smooth', 'block': 'center'})

  # ------------------------------------------------------------ render
  def _render(self, just_sent):
    unlocked = bool(self.links)
    ui.show(self.form.querySelector('.form-body'), not unlocked)
    ui.show(self.form.querySelector('.ok'), unlocked)
    ui.show(self.form.querySelector('.js-sent'), just_sent)
    if unlocked:
      self.form.querySelector('.js-list').innerHTML = ''.join(
        f'<div class="row"><span><i>{num}</i>{t(title)}</span>{_download(slug, self.links[slug], title, "sm")}</div>'
        for slug, num, title, hook, inside, pages in GUIDES if slug in self.links)
    cards = ''
    for slug, num, title, hook, inside, pages in GUIDES:
      if unlocked and slug in self.links:
        act = _download(slug, self.links[slug], title)
      else:
        act = f'<button type="button" class="aa-btn sm" data-act="want" data-arg="{slug}">{t("Get it free")} <span class="arr">&rarr;</span></button>'
      ticks = ''.join(f'<li>{icon("check", "width=15 height=15")}<span>{t(x)}</span></li>' for x in inside)
      cards += f'''
        <article class="gd-card rv{" focus" if slug == self.focus else ""}" id="g-{slug}">
          <img src="{guide_cover(slug)}" alt="{ui.esc(t('Cover of the guide {title}', title=t(title)))}" loading="lazy" decoding="async" width="480" height="621">
          <div class="b">
            <div class="meta">{num} · {t('PDF · {n} pages', n=pages)}</div>
            <h3>{t(title)}</h3>
            <p class="hook">{t(hook)}</p>
            <ul>{ticks}</ul>
            <div class="act">{act}</div>
          </div>
        </article>'''
    self.node.querySelector('.js-cards').innerHTML = cards
    ui.reveal(self)

  # ------------------------------------------------------------ actions
  def _want(self, slug):
    self.focus = slug if slug in GUIDE_SLUGS else self.focus
    self.form.scrollIntoView({'behavior': 'smooth', 'block': 'center'})
    box = self.form.querySelector('#gd-email')
    if box is not None:
      box.focus({'preventScroll': True})

  def _submit(self):
    v = ui.vals(self.form)
    err = self.form.querySelector('.aa-error')

    def fail(msg):
      err.textContent = msg
      ui.show(err)

    email = v.get('email', '')
    if '@' not in email or '.' not in email.split('@')[-1]:
      return fail(t("Please enter a valid email address."))
    ui.show(err, False)
    v['guide'] = self.focus
    v['lang'] = i18n.lang
    btn = self.form.querySelector('[data-act=get]')
    ui.busy(btn, True, t('Sending…'))
    res = ui.call('request_guides', v)
    ui.busy(btn, False)
    if res is ui.FAIL or not res:
      return
    self.links = {slug: url for slug, url in res.get('links', [])}
    _save(self.links)
    self._render(just_sent=bool(res.get('emailed')))
    self.form.scrollIntoView({'behavior': 'smooth', 'block': 'center'})
