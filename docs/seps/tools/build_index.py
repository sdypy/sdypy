"""
Scan the directory of sep files and extract their metadata.  The
metadata is passed to Jinja for filling out `index.rst.tmpl`.¸

Acknowledgement: 
this document is heavily based on 
https://github.com/numpy/numpy/blob/master/doc/neps/tools/build_index.py
"""

import os
import jinja2
import glob
import re


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)

def sep_metadata():
    ignore = ('sep-template.rst')
    sources = sorted(glob.glob(r'sep-*.rst'))
    sources = [s for s in sources if not s in ignore]

    meta_re = r':([a-zA-Z\-]*): (.*)'

    has_provisional = False
    seps = {}
    print('Loading metadata for:')
    for source in sources:
        print(f' - {source}')
        nr = int(re.match(r'sep-([0-9]{4}).*\.rst', source).group(1))

        with open(source) as f:
            lines = f.readlines()
            tags = [re.match(meta_re, line) for line in lines]
            tags = [match.groups() for match in tags if match is not None]
            tags = {tag[0]: tag[1] for tag in tags}

            # The title should be the first line after a line containing only
            # * or = signs.
            for i, line in enumerate(lines[:-1]):
                chars = set(line.rstrip())
                if len(chars) == 1 and ("=" in chars or "*" in chars):
                    break
            else:
                raise RuntimeError("Unable to find SEP title.")

            tags['Title'] = lines[i+1].strip()
            tags['Filename'] = source

        if not tags['Title'].startswith(f'SEP {nr} — '):
            raise RuntimeError(
                f'Title for SEP {nr} does not start with "SEP {nr} — " '
                '(note that — here is a special, enlongated dash). Got: '
                f'    {tags["Title"]!r}')

        if tags['Status'] in ('Accepted', 'Rejected', 'Withdrawn'):
            if not 'Resolution' in tags:
                raise RuntimeError(
                    f'SEP {nr} is Accepted/Rejected/Withdrawn but '
                    'has no Resolution tag'
                )
        if tags['Status'] == 'Provisional':
            has_provisional = True

        seps[nr] = tags

    # Now that we have all of the SEP metadata, do some global consistency
    # checks

    for nr, tags in seps.items():
        if tags['Status'] == 'Superseded':
            if not 'Replaced-By' in tags:
                raise RuntimeError(
                    f'SEP {nr} has been Superseded, but has no Replaced-By tag'
                )

            replaced_by = int(tags['Replaced-By'])
            replacement_sep = seps[replaced_by]

            if not 'Replaces' in replacement_sep:
                raise RuntimeError(
                    f'SEP {nr} is superseded by {replaced_by}, but that SEP has '
                    f"no Replaces tag."
                )

            if not int(replacement_sep['Replaces']) == nr:
                raise RuntimeError(
                    f'SEP {nr} is superseded by {replaced_by}, but that SEP has a '
                    f"Replaces tag of `{replacement_sep['Replaces']}`."
                )

        if 'Replaces' in tags:
            replaced_sep = int(tags['Replaces'])
            replaced_sep_tags = seps[replaced_sep]
            if not replaced_sep_tags['Status'] == 'Superseded':
                raise RuntimeError(
                    f'SEP {nr} replaces {replaced_sep}, but that SEP has not '
                    f'been set to Superseded'
                )

    return {'seps': seps, 'has_provisional': has_provisional}


infile = 'index.rst.tmpl'
outfile = 'index.rst'

meta = sep_metadata()

print(f'Compiling {infile} -> {outfile}')
index = render(infile, meta)

with open(outfile, 'w') as f:
    f.write(index)
