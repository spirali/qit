
#ifndef QIT_WRITE_H
#define QIT_WRITE_H

#include <stdio.h>
#include <vector>

namespace qit {

template<typename T> void write(FILE *out, T value)
{
    value.write(out);
}

template<> void write<int>(FILE *out, int value)
{
    fwrite(&value, sizeof(int), 1, out);
}

template<> void write<bool>(FILE *out, bool value)
{
    fwrite(&value, sizeof(bool), 1, out);
}

template<typename T>
void write(FILE *out, const std::vector<T> &value)
{
    size_t size = value.size();
    fwrite(&size, sizeof(size_t), 1, out);
    typename std::vector<T>::const_iterator i;
    for (i = value.begin(); i != value.end(); i++) {
        write(out, *i);
    }
}


#define QIT_ITERATOR_WRITE_METHOD \
    void write(FILE *f) { \
	value_type v; \
	char flag = 1; \
	while (next(v)) { \
	    fwrite(&flag, 1, 1, f); \
	    qit::write(f, v); \
	} \
	flag = 0; \
	fwrite(&flag, 1, 1, f); \
    }

}

#endif
