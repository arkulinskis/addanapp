"""Ads (#apps/ads[/<doc>]): ready-to-run Meta and Google ads for every app, made on the PC (APP_MAKER/ads, 2026-11-27).

The PC pushes per client: docs 'ads/index' (the ranked list), 'ads/<key>' (one app: competitors and their long-running
ads, 5 concepts with images, copy, targeting, Google keywords) and 'ads/GUIDE' (how to run ads, markdown). Images live
on the media Worker (R2), so only their addresses are stored here. Comments go in as "Changes for Claude" requests on
the app (api_apps.apps_add_change), so they reach the PC like every other change.
"""
import html
import re

import anvil.server

from . import apps_core as core
from .api_apps import _client

KEY = re.compile(r'[a-z0-9:_-]{1,60}')
PRIORITY = {1: ('Run first', 'p1'), 2: ('Next', 'p2'), 3: ('Later', 'p3')}


def e(s):
  return html.escape(str(s if s is not None else ''))


def _copy(label, text):
  """A labelled text block with a Copy button (the page copies data-copy)."""
  if not text:
    return ''
  return ('<div class="ad-field"><div class="ad-fl"><span>%s</span><button type="button" class="ad-copy" data-copy="%s">Copy</button></div>'
          '<div class="ad-fv">%s</div></div>') % (e(label), e(text), e(text).replace('\n', '<br>'))


def _list_copy(label, items, limit=None):
  items = [str(x) for x in items or [] if x]
  if not items:
    return ''
  lis = ''.join('<li>%s%s</li>' % (e(x), (' <span class="ad-n">%d</span>' % len(x)) if limit else '') for x in items)
  return ('<div class="ad-field"><div class="ad-fl"><span>%s</span><button type="button" class="ad-copy" data-copy="%s">Copy all</button></div>'
          '<ul class="ad-ul">%s</ul></div>') % (e(label), e('\n'.join(items)), lis)


def _concept(c):
  m = c.get('meta') or {}
  img = c.get('img') or {}
  pics = ''
  for size, label in (('feed', 'Feed 4:5'), ('story', 'Story 9:16')):
    p = img.get(size) or {}
    if p.get('thumb'):
      pics += ('<figure class="ad-pic ad-%s"><a href="%s" target="_blank" rel="noopener"><img loading="lazy" src="%s" alt="%s ad %s"></a>'
               '<figcaption>%s · <a href="%s?dl=1">Download</a></figcaption></figure>') % (
        size, e(p.get('full')), e(p.get('thumb')), e(label), e(c.get('id')), e(label), e(p.get('full')))
  check = '<p class="ad-check"><b>Check before running:</b> %s</p>' % e(c['check']) if c.get('check') else ''
  return ('<article class="ad-concept" id="ad-%s"><div class="ad-pics">%s</div><div class="ad-copyside">'
          '<div class="ad-ch"><span class="ad-id">%s</span><span class="ad-angle">%s</span><span class="ad-tpl">%s</span></div>'
          '%s%s%s%s%s'
          '<p class="ad-why"><b>Why:</b> %s</p><p class="ad-why"><b>Test:</b> %s</p>%s</div></article>') % (
    e(c.get('id')), pics, e(str(c.get('id', '')).upper()), e(c.get('angle')), e(c.get('template')),
    _copy('Primary text', m.get('primary_text')), _copy('Headline', m.get('headline')), _copy('Description', m.get('description')),
    _copy('Button', m.get('cta_button')), _copy('Link (with tracking)', c.get('link')),
    e(c.get('why')), e(c.get('hypothesis')), check)


def app_html(d):
  pr = PRIORITY.get(d.get('priority'), ('', 'p3'))
  head = ('<div class="ad-head"><span class="ad-pri %s">%s</span><h2>%s</h2><a href="%s" target="_blank" rel="noopener">%s</a></div>'
          '<p class="ad-offer"><b>Offer:</b> %s</p><p><b>Audience:</b> %s</p>%s'
          '<div class="ad-insight"><b>What the competitors\' long-running ads teach</b><p>%s</p></div>') % (
    pr[1], e(pr[0]), e(d.get('name')), e(d.get('url')), e((d.get('url') or '').split('//')[-1].strip('/')),
    e(d.get('offer')), e(d.get('audience')), ('<p class="ad-muted">%s</p>' % e(d['priority_why'])) if d.get('priority_why') else '',
    e(d.get('insight')))
  comps = ''
  for c in d.get('competitors') or []:
    a = c.get('adlib') or {}
    tops = ''.join('<li><span class="ad-days">%s days</span> %s</li>' % (e(t.get('days')), e(t.get('text'))) for t in (a.get('top') or [])[:3])
    shot = ('<a class="ad-shot" href="%s" target="_blank" rel="noopener"><img loading="lazy" src="%s" alt="%s ads in the Meta Ad Library"></a>' % (
      e(a['shot']), e(a['shot']), e(c.get('name')))) if a.get('shot') else ''
    lib = '<a href="%s" target="_blank" rel="noopener">Their ads in the Meta Ad Library ↗</a>' % e(a['link']) if a.get('link') else ''
    if a.get('long_count'):
      found = '%s ads running 90+ days (the ones that earn their keep)' % e(a['long_count'])
    elif a.get('kind') == 'active' and tops:
      found = '%s Their most-seen ads right now:' % e(a.get('note') or 'No ads running 90+ days.')
    else:
      found = e(a.get('note') or 'No long-running ads found.')
    comps += ('<div class="ad-comp">%s<div><h4>%s <span class="ad-price">%s</span></h4><p>%s</p><p><b>Lesson:</b> %s</p>'
              '<p class="ad-muted">%s%s</p><ul class="ad-tops">%s</ul>%s</div></div>') % (
      shot, e(c.get('name')), e(c.get('price')), e(c.get('long_running')), e(c.get('lesson')),
      found, (' · price checked: ' + e(c['price_source'])) if c.get('price_source') else '', tops, lib)
  concepts = ''.join(_concept(c) for c in d.get('concepts') or [])
  t = d.get('targeting') or {}
  targ = ''.join('<tr><th>%s</th><td>%s</td></tr>' % (e(k.capitalize()), e(v)) for k, v in t.items() if v)
  g = d.get('google') or {}
  google = ''
  if g.get('headlines'):
    google = ('<h3>Google Search ad</h3><div class="ad-google">%s%s%s%s</div>') % (
      _list_copy('Keywords', g.get('keywords')), _list_copy('Negative keywords', g.get('negatives')),
      _list_copy('Headlines (max 30 characters)', g.get('headlines'), 30), _list_copy('Descriptions (max 90)', g.get('descriptions'), 90))
  notes = ''.join('<li>%s</li>' % e(n) for n in d.get('notes') or [])
  return (head + '<h3>The 5 ads</h3><p class="ad-muted">Click a picture for full size. Upload the Feed picture and, for Stories and Reels, '
          'the Story picture in the same ad. Copy each text into Ads Manager.</p>' + concepts +
          ('<h3>Who to show them to</h3><table class="ad-targ">%s</table>' % targ if targ else '') + google +
          ('<h3>Notes</h3><ul>%s</ul>' % notes if notes else '') +
          '<h3>Competitors and their ads</h3>' + comps +
          '<p class="ad-muted">Made %s. Ask Claude to change anything with the box below.</p>' % e(d.get('made')))


@anvil.server.callable
def apps_ads(name='GUIDE', client_id=None):
  """The Ads view: the ranked app list + the guide (markdown as HTML) or one app's ads page."""
  _u, client = _client(client_id)
  idx = core.doc_data(client, 'ads/index', {}) or {}
  name = str(name or 'GUIDE')
  if name != 'GUIDE' and not KEY.fullmatch(name):
    name = 'GUIDE'
  out = {'apps': idx.get('apps') or [], 'made': idx.get('made'), 'name': name, 'html': '', 'concepts': [], 'missing': False}
  if name == 'GUIDE':
    text = core.doc_text(client, 'ads/GUIDE')
    out['missing'] = not text
    out['html'] = core.markdown(text, 'ads')
  else:
    d = core.doc_data(client, 'ads/' + name, None)
    out['missing'] = not d
    if d:
      out['html'] = app_html(d)
      out['concepts'] = [[c.get('id'), '%s · %s' % (str(c.get('id', '')).upper(), c.get('angle') or c.get('template'))] for c in d.get('concepts') or []]
  return out
